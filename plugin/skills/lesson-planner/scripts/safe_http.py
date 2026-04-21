"""Minimal HTTP(S) fetch helper with IP pinning for SSRF resistance.

This module resolves a hostname once, rejects private/loopback/link-local
targets, and then connects directly to the resolved public IP while sending
the original Host header and (for HTTPS) using the original hostname for SNI
and certificate validation. That closes the DNS-rebinding window left by
``requests.get(url)`` after a separate preflight resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urlparse


REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_IP_ADDRESS_TYPES = (ipaddress.IPv4Address, ipaddress.IPv6Address)


class BodyTooLargeError(RuntimeError):
    """Raised when a response body exceeds the caller's byte budget."""


@dataclass(frozen=True)
class ValidatedURL:
    """Pinned connection metadata returned by ``validate_url``."""

    url: str
    parsed: object
    hostname: str
    port: int
    connect_host: str


def _is_forbidden_ip(addr: object) -> bool:
    if not isinstance(addr, _IP_ADDRESS_TYPES):
        raise TypeError(f"Expected ipaddress object, got {type(addr).__name__}")
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def is_private_ip(hostname: str) -> bool:
    """Resolve hostname and reject private/loopback/link-local addresses."""
    try:
        infos = socket.getaddrinfo(
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )
    except socket.gaierror:
        return True

    for _, _, _, _, sockaddr in infos:
        addr = ipaddress.ip_address(sockaddr[0])
        if _is_forbidden_ip(addr):
            return True
    return False


def resolve_public_ip(hostname: str, port: int) -> str:
    """Resolve ``hostname`` and return a single public IP string.

    Any private/loopback/link-local answer causes a hard failure. A mixed
    public/private answer set is treated as unsafe rather than trying to pick
    the "good" answer and hoping the resolver stays stable.
    """
    try:
        infos = socket.getaddrinfo(
            hostname,
            port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise ValueError(f"Blocked unresolved target: {hostname}") from exc

    public_ips: list[str] = []
    for _, _, _, _, sockaddr in infos:
        addr = ipaddress.ip_address(sockaddr[0])
        if _is_forbidden_ip(addr):
            raise ValueError(f"Blocked private/loopback target: {hostname}")
        public_ips.append(sockaddr[0])

    if not public_ips:
        raise ValueError(f"Blocked unresolved target: {hostname}")
    return public_ips[0]


def validate_url(url: str) -> ValidatedURL:
    """Block non-http(s) schemes and return a pinned public target."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Blocked scheme: {parsed.scheme}")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("No hostname in URL")
    port = parsed.port or default_port(parsed.scheme)
    return ValidatedURL(
        url=url,
        parsed=parsed,
        hostname=hostname,
        port=port,
        connect_host=resolve_public_ip(hostname, port),
    )


def default_port(scheme: str) -> int:
    return 443 if scheme == "https" else 80


def request_target(parsed) -> str:
    target = parsed.path or "/"
    if parsed.params:
        target += f";{parsed.params}"
    if parsed.query:
        target += f"?{parsed.query}"
    return target


def host_header(parsed) -> str:
    host = parsed.hostname or ""
    port = parsed.port
    if port is None or port == default_port(parsed.scheme):
        return host
    return f"{host}:{port}"


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection that dials a pinned IP but validates the hostname."""

    def __init__(
        self,
        connect_host: str,
        port: int,
        timeout: float,
        server_hostname: str,
    ) -> None:
        self._connect_host = connect_host
        self._server_hostname = server_hostname
        context = ssl.create_default_context()
        super().__init__(
            connect_host,
            port=port,
            timeout=timeout,
            context=context,
        )

    def connect(self) -> None:
        sock = socket.create_connection(
            (self._connect_host, self.port),
            self.timeout,
            self.source_address,
        )
        self.sock = self._context.wrap_socket(
            sock,
            server_hostname=self._server_hostname,
        )


def open_connection(
    scheme: str,
    connect_host: str,
    port: int,
    server_hostname: str,
    timeout: float,
):
    if scheme == "https":
        return PinnedHTTPSConnection(
            connect_host=connect_host,
            port=port,
            timeout=timeout,
            server_hostname=server_hostname,
        )
    return http.client.HTTPConnection(connect_host, port=port, timeout=timeout)


def fetch_url(
    url: str | ValidatedURL,
    *,
    timeout: float,
    user_agent: str,
    extra_headers: dict[str, str] | None = None,
    max_body_bytes: int | None = None,
) -> tuple[int, dict[str, str], bytes]:
    """Fetch a URL without following redirects.

    Returns ``(status_code, headers, body)``. The TCP/TLS connection is pinned
    to the previously validated public IP so rebinding cannot change the
    destination after validation. If ``max_body_bytes`` is set, the body is
    read in chunks and the fetch aborts once the limit is exceeded.
    """
    validated = url if isinstance(url, ValidatedURL) else validate_url(url)
    parsed = validated.parsed
    headers = {
        "Host": host_header(parsed),
        "User-Agent": user_agent,
        "Accept-Encoding": "identity",
        "Connection": "close",
    }
    if extra_headers:
        headers.update(extra_headers)

    conn = open_connection(
        parsed.scheme,
        validated.connect_host,
        validated.port,
        validated.hostname,
        timeout,
    )
    try:
        conn.request("GET", request_target(parsed), headers=headers)
        resp = conn.getresponse()
        body = _read_body(resp, max_body_bytes=max_body_bytes)
        return resp.status, dict(resp.getheaders()), body
    finally:
        conn.close()


def _read_body(resp, *, max_body_bytes: int | None) -> bytes:
    if max_body_bytes is None:
        return resp.read()

    chunks: list[bytes] = []
    total = 0
    chunk_size = 64 * 1024

    while True:
        # Read one byte past the remaining budget so exact-limit bodies pass
        # cleanly while limit+1 bodies deterministically raise.
        remaining = max_body_bytes - total + 1
        chunk = resp.read(min(chunk_size, remaining))
        if not chunk:
            break
        total += len(chunk)
        if total > max_body_bytes:
            raise BodyTooLargeError(
                f"Response body exceeded {max_body_bytes} bytes"
            )
        chunks.append(chunk)

    return b"".join(chunks)
