"""Tests for safe_http.py — pinned-IP fetch semantics."""

from __future__ import annotations

import ipaddress
import socket

import pytest

import safe_http


class _FakeResponse:
    def __init__(self, status=200, headers=None, body=b"ok"):
        self.status = status
        self._headers = headers or {"Content-Type": "text/plain"}
        self._body = body
        self._offset = 0

    def getheaders(self):
        return list(self._headers.items())

    def read(self, amt=None):
        if self._offset >= len(self._body):
            return b""
        if amt is None:
            chunk = self._body[self._offset:]
            self._offset = len(self._body)
            return chunk
        start = self._offset
        end = min(len(self._body), start + amt)
        self._offset = end
        return self._body[start:end]


class _OneByteResponse(_FakeResponse):
    def read(self, amt=None):
        if amt is not None:
            amt = min(amt, 1)
        return super().read(amt)


class _FakeConnection:
    def __init__(self, response):
        self.response = response
        self.request_calls = []
        self.closed = False

    def request(self, method, target, headers=None):
        self.request_calls.append((method, target, headers or {}))

    def getresponse(self):
        return self.response

    def close(self):
        self.closed = True


class TestIpFiltering:
    @pytest.mark.parametrize(
        ("ip_text", "expected"),
        [
            ("127.0.0.1", True),
            ("::1", True),
            ("fe80::1", True),
            ("172.16.0.1", True),
            ("192.168.1.20", True),
            ("224.0.0.1", True),
            ("0.0.0.0", True),
            ("8.8.8.8", False),
            ("2606:4700:4700::1111", False),
        ],
    )
    def test_is_forbidden_ip_covers_private_loopback_link_local_and_multicast(
        self, ip_text, expected
    ):
        assert safe_http._is_forbidden_ip(ipaddress.ip_address(ip_text)) is expected


class TestDnsResolution:
    def test_is_private_ip_rejects_mixed_public_private_answers(self, monkeypatch):
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.50", 0)),
            ],
        )

        assert safe_http.is_private_ip("example.gov") is True

    def test_is_private_ip_rejects_ipv6_loopback(self, monkeypatch):
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 0, 0, 0)),
            ],
        )

        assert safe_http.is_private_ip("example.gov") is True

    def test_is_private_ip_all_public_answers_pass(self, monkeypatch):
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
                (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:4700:4700::1111", 0, 0, 0)),
            ],
        )

        assert safe_http.is_private_ip("example.gov") is False

    def test_resolve_public_ip_rejects_mixed_public_private_answers(self, monkeypatch):
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("172.16.1.9", 443)),
            ],
        )

        with pytest.raises(ValueError, match="Blocked private/loopback target"):
            safe_http.resolve_public_ip("example.gov", 443)

    def test_resolve_public_ip_rejects_ipv6_link_local(self, monkeypatch):
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fe80::abcd", 443, 0, 0)),
            ],
        )

        with pytest.raises(ValueError, match="Blocked private/loopback target"):
            safe_http.resolve_public_ip("example.gov", 443)

    def test_resolve_public_ip_returns_first_public_answer(self, monkeypatch):
        monkeypatch.setattr(
            socket,
            "getaddrinfo",
            lambda *args, **kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.4.4", 443)),
            ],
        )

        assert safe_http.resolve_public_ip("example.gov", 443) == "8.8.8.8"

    def test_validate_url_uses_socket_resolution_not_stubbed_public_ip(self, monkeypatch):
        seen = []

        def fake_getaddrinfo(hostname, port, family, socktype):
            seen.append((hostname, port, family, socktype))
            return [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", port)),
            ]

        monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

        validated = safe_http.validate_url("https://example.gov/resource")

        assert validated.connect_host == "8.8.8.8"
        assert seen == [("example.gov", 443, socket.AF_UNSPEC, socket.SOCK_STREAM)]


class TestFetchUrl:
    def test_fetch_pins_resolved_ip_and_preserves_host_header(self, monkeypatch):
        opened = {}
        fake_conn = _FakeConnection(_FakeResponse())

        monkeypatch.setattr(
            safe_http,
            "resolve_public_ip",
            lambda hostname, port: "203.0.113.10",
        )

        def fake_open_connection(scheme, connect_host, port, server_hostname, timeout):
            opened.update({
                "scheme": scheme,
                "connect_host": connect_host,
                "port": port,
                "server_hostname": server_hostname,
                "timeout": timeout,
            })
            return fake_conn

        monkeypatch.setattr(safe_http, "open_connection", fake_open_connection)

        status, headers, body = safe_http.fetch_url(
            "https://example.gov/path/to/resource?q=1",
            timeout=7,
            user_agent="LessonPlanMagic/Test",
        )

        assert status == 200
        assert headers["Content-Type"] == "text/plain"
        assert body == b"ok"
        assert opened == {
            "scheme": "https",
            "connect_host": "203.0.113.10",
            "port": 443,
            "server_hostname": "example.gov",
            "timeout": 7,
        }
        assert fake_conn.request_calls == [
            (
                "GET",
                "/path/to/resource?q=1",
                {
                    "Host": "example.gov",
                    "User-Agent": "LessonPlanMagic/Test",
                    "Accept-Encoding": "identity",
                    "Connection": "close",
                },
            )
        ]
        assert fake_conn.closed is True

    def test_fetch_preserves_nondefault_port_in_host_header(self, monkeypatch):
        fake_conn = _FakeConnection(_FakeResponse())

        monkeypatch.setattr(
            safe_http,
            "resolve_public_ip",
            lambda hostname, port: "203.0.113.20",
        )
        monkeypatch.setattr(
            safe_http,
            "open_connection",
            lambda scheme, connect_host, port, server_hostname, timeout: fake_conn,
        )

        safe_http.fetch_url(
            "http://example.com:8080/path",
            timeout=5,
            user_agent="LessonPlanMagic/Test",
        )

        _, _, headers = fake_conn.request_calls[0]
        assert headers["Host"] == "example.com:8080"

    def test_fetch_uses_prevalidated_target_without_reresolving(self, monkeypatch):
        fake_conn = _FakeConnection(_FakeResponse())
        resolve_calls = []

        def fake_resolve(hostname, port):
            resolve_calls.append((hostname, port))
            return "203.0.113.30"

        monkeypatch.setattr(safe_http, "resolve_public_ip", fake_resolve)
        monkeypatch.setattr(
            safe_http,
            "open_connection",
            lambda scheme, connect_host, port, server_hostname, timeout: fake_conn,
        )

        validated = safe_http.validate_url("https://example.edu/resource")
        safe_http.fetch_url(
            validated,
            timeout=5,
            user_agent="LessonPlanMagic/Test",
        )

        assert resolve_calls == [("example.edu", 443)]

    def test_fetch_rejects_oversized_body(self, monkeypatch):
        fake_conn = _FakeConnection(_FakeResponse(body=b"x" * 11))

        monkeypatch.setattr(
            safe_http,
            "resolve_public_ip",
            lambda hostname, port: "203.0.113.40",
        )
        monkeypatch.setattr(
            safe_http,
            "open_connection",
            lambda scheme, connect_host, port, server_hostname, timeout: fake_conn,
        )

        with pytest.raises(safe_http.BodyTooLargeError):
            safe_http.fetch_url(
                "https://example.gov/large",
                timeout=5,
                user_agent="LessonPlanMagic/Test",
                max_body_bytes=10,
            )

        assert fake_conn.closed is True

    def test_fetch_accepts_body_exactly_at_limit(self, monkeypatch):
        fake_conn = _FakeConnection(_FakeResponse(body=b"x" * 10))

        monkeypatch.setattr(
            safe_http,
            "resolve_public_ip",
            lambda hostname, port: "203.0.113.41",
        )
        monkeypatch.setattr(
            safe_http,
            "open_connection",
            lambda scheme, connect_host, port, server_hostname, timeout: fake_conn,
        )

        status, headers, body = safe_http.fetch_url(
            "https://example.gov/exact",
            timeout=5,
            user_agent="LessonPlanMagic/Test",
            max_body_bytes=10,
        )

        assert status == 200
        assert headers["Content-Type"] == "text/plain"
        assert body == b"x" * 10

    def test_fetch_accepts_body_exactly_at_limit_when_streamed(self, monkeypatch):
        fake_conn = _FakeConnection(_OneByteResponse(body=b"x" * 10))

        monkeypatch.setattr(
            safe_http,
            "resolve_public_ip",
            lambda hostname, port: "203.0.113.42",
        )
        monkeypatch.setattr(
            safe_http,
            "open_connection",
            lambda scheme, connect_host, port, server_hostname, timeout: fake_conn,
        )

        status, headers, body = safe_http.fetch_url(
            "https://example.gov/streamed-exact",
            timeout=5,
            user_agent="LessonPlanMagic/Test",
            max_body_bytes=10,
        )

        assert status == 200
        assert headers["Content-Type"] == "text/plain"
        assert body == b"x" * 10
