#!/usr/bin/env python3
"""Verify URLs for K-12 lesson plan citation safety.

Output discipline: stdout returns ONLY the fields the plan pipeline needs
({url, verified, reason}). Cache files on disk are dense JSON (no indent)
keyed for 30-day TTL. Human debugging detail (domain, title match score,
allowlist hit, status code) is kept in cache but NOT echoed to stdout —
the downstream consumer is Claude, which pays tokens per echoed field.
Pass --verbose to surface the full record.
"""

from __future__ import annotations

import json
import re
import sys
import hashlib
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from rapidfuzz.fuzz import token_set_ratio

import safe_http

# Stopwords pruned from the claimed title before computing content-token
# recall. Keeping the list tight (articles, prepositions, conjunctions)
# avoids dropping subject-distinctive short words like "war" or "dna".
_TITLE_STOPWORDS = frozenset({
    "the", "a", "an", "of", "and", "or", "to", "in", "on", "for",
    "at", "is", "are", "be", "this", "that", "with", "by", "from",
    "as", "into", "via", "vs", "but",
})

ALLOWLIST = {
    "loc.gov", "si.edu", "archives.gov",
    "pbslearningmedia.org", "nasa.gov", "noaa.gov", "nih.gov", "cdc.gov",
    "khanacademy.org", "commonlit.org", "newsela.com", "readworks.org",
    "edsitement.neh.gov", "brainpop.com",
    # Public broadcasters: .co.uk only (BBC News .com is a clickbait-
    # heavier US feed). NPR and PBS .org are the US equivalents.
    "npr.org", "pbs.org", "bbc.co.uk",
    "americanhistory.si.edu", "smithsonianmag.com",
}

# Domains that require a title match to verify (not blanket-trusted).
# Allows them through if the claimed_title matches the page title, but
# not just on domain alone.
REQUIRES_TITLE_MATCH = {
    "ted.com",       # conditional allow via title match only
    "teded.com",     # conditional allow via title match only
    "bbc.com",       # conditional allow via title match only
}

ALLOWLIST_TLDS = (".gov", ".edu", ".mil")
ALLOWLIST_TITLE_MATCH_THRESHOLD = 0.65
NON_ALLOWLIST_TITLE_MATCH_THRESHOLD = 0.75
CONDITIONAL_TITLE_BRANDS = frozenset({
    "ted", "ted ed", "teded", "bbc", "bbc bitesize", "bitesize",
})

# .gov politeness: back off on burst 429s rather than hammering.
GOV_MAX_CONCURRENT = 3
GOV_BACKOFF_SECONDS = (1.0, 3.0, 8.0)  # exponential-ish retry
MAX_FETCH_BYTES = 2 * 1024 * 1024
BATCH_RESULT_TIMEOUT_SECONDS = 30
BATCH_MAX_WORKERS = 8
BATCH_POLL_INTERVAL_SECONDS = 0.05

BLOCKLIST = {
    "pinterest.com", "teacherspayteachers.com",
    "reddit.com", "quora.com", "wikihow.com",
}


def normalize_domain(url: str) -> str:
    """Extract and normalize domain from URL.

    Uses ``parsed.hostname`` (not ``netloc``) so port and userinfo are
    stripped — without this, ``https://reddit.com:443/...`` would become
    ``reddit.com:443`` and bypass both the BLOCKLIST and the explicit
    allowlist match.
    """
    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def matches_allowlist(domain: str) -> bool:
    """Check if domain matches allowlist (exact or TLD).

    Domains in REQUIRES_TITLE_MATCH are NOT blanket-allowed — they only
    pass verification if the fetched page title matches the claimed title.
    """
    if domain in REQUIRES_TITLE_MATCH:
        return False
    if domain in ALLOWLIST:
        return True
    for tld in ALLOWLIST_TLDS:
        if domain.endswith(tld):
            return True
    return False


def requires_title_match(domain: str) -> bool:
    """Domain is conditionally trusted — needs a title match to verify."""
    return domain in REQUIRES_TITLE_MATCH


def is_blocklisted(domain: str) -> bool:
    """Check if domain is blocklisted."""
    return domain in BLOCKLIST or any(domain.endswith(f".{b}") for b in BLOCKLIST)


def _is_private_ip(hostname: str) -> bool:
    """Resolve hostname and reject private/loopback/link-local addresses."""
    return safe_http.is_private_ip(hostname)


def _validate_fetch_url(url: str) -> safe_http.ValidatedURL:
    """Pre-flight check: scheme + private-host filter + pinned IP."""
    return safe_http.validate_url(url)


def fetch_title(url: str) -> tuple[int, str]:
    """Fetch page and extract title. Returns (status_code, title).

    Pre-validates the URL against private networks and re-checks after
    every redirect hop so a 302 can't bounce to loopback.
    For .gov domains, retry once on 429 with a backoff per GOV_BACKOFF_SECONDS.
    """
    # --- Pre-fetch safety gate ---
    try:
        initial_target = _validate_fetch_url(url)
    except ValueError as exc:
        return 0, f"fetch blocked: {str(exc).lower()}"

    domain = normalize_domain(url)
    is_gov = domain.endswith(".gov")
    attempts = len(GOV_BACKOFF_SECONDS) if is_gov else 1

    for attempt in range(attempts):
        try:
            current_target = initial_target
            current_url = current_target.url
            # Disable auto-redirects so we can validate each hop and pin each
            # hop's TCP/TLS connection to the validated public IP.
            status, headers, body = safe_http.fetch_url(
                current_target,
                timeout=10,
                user_agent="LessonPlanMagic/0.2",
                max_body_bytes=MAX_FETCH_BYTES,
            )
            # Manually follow redirects with revalidation
            hops = 0
            while status in safe_http.REDIRECT_STATUSES and hops < 5:
                from urllib.parse import urljoin
                next_url = urljoin(current_url, headers.get("Location", ""))
                try:
                    current_target = _validate_fetch_url(next_url)
                except ValueError as exc:
                    return 0, f"fetch blocked on redirect: {str(exc).lower()}"
                status, headers, body = safe_http.fetch_url(
                    current_target,
                    timeout=10,
                    user_agent="LessonPlanMagic/0.2",
                    max_body_bytes=MAX_FETCH_BYTES,
                )
                current_url = current_target.url
                hops += 1

            if status == 200:
                soup = BeautifulSoup(body, "html.parser")
                title = soup.title.string.strip() if soup.title else ""
                return status, title
            if status == 429 and is_gov and attempt < attempts - 1:
                time.sleep(GOV_BACKOFF_SECONDS[attempt])
                continue
            return status, ""
        except safe_http.BodyTooLargeError as exc:
            return 0, f"fetch blocked: {str(exc).lower()}"
        except Exception as e:
            if is_gov and attempt < attempts - 1:
                time.sleep(GOV_BACKOFF_SECONDS[attempt])
                continue
            return 0, f"fetch error: {type(e).__name__}"
    return 0, "fetch error: retries exhausted"


def _content_token_recall(claimed: str, actual: str) -> float:
    """Fraction of the claimed title's distinctive content tokens present
    in the actual title. "Distinctive" = length >= 3 and not a stopword.

    Pure token_set_ratio over-weights shared stopwords and the generic
    label word(s), producing false positives like
    ``"Expected Title" vs "Wrong Title"`` (shared "title" → 0.62) or
    ``"Newtons Laws of Motion" vs "Laws of Motion Worksheet"`` (shared
    "laws/of/motion" → 0.78). Requiring content tokens to actually appear
    in the actual title closes that bypass without hurting legitimate
    matches — those keep recall == 1.0.
    """
    claimed_tokens = [
        t for t in re.findall(r"[a-z0-9]+", claimed.lower())
        if t not in _TITLE_STOPWORDS and len(t) >= 3
    ]
    if not claimed_tokens:
        return 1.0
    actual_tokens = set(re.findall(r"[a-z0-9]+", actual.lower()))
    present = sum(1 for t in claimed_tokens if t in actual_tokens)
    return present / len(claimed_tokens)


def fuzzy_title_match(claimed: str, actual: str) -> float:
    """Return a conservative title match score (0-1).

    Combines token_set_ratio (loose, order-insensitive overlap) with
    content-token recall (strict, counts distinctive claimed tokens that
    actually appear in actual). Uses min() so BOTH must be high — this
    prevents shared filler words from dragging the score above threshold
    when the distinctive claimed tokens are missing.
    """
    if not claimed or not actual:
        return 0.0
    set_score = token_set_ratio(claimed.lower(), actual.lower()) / 100.0
    recall = _content_token_recall(claimed, actual)
    return min(set_score, recall)


def _normalize_title_text(title: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", title.lower()))


def _canonicalize_conditional_title(title: str) -> str:
    parts = [
        _normalize_title_text(part)
        for part in re.split(r"\s*(?:\||:|—|–|\s-\s)\s*", title)
        if part.strip()
    ]
    while parts and parts[0] in CONDITIONAL_TITLE_BRANDS:
        parts.pop(0)
    while parts and parts[-1] in CONDITIONAL_TITLE_BRANDS:
        parts.pop()
    return " ".join(parts).strip()


def _strict_conditional_title_match(claimed: str, actual: str) -> bool:
    """Require a strong title match for conditionally trusted domains."""
    norm_claimed = _canonicalize_conditional_title(claimed)
    norm_actual = _canonicalize_conditional_title(actual)
    if not norm_claimed or not norm_actual:
        return False
    return norm_claimed == norm_actual


def _title_cache_slug(claimed_title: str | None) -> str:
    """Short fingerprint of a claimed_title for the cache key.

    Two calls that claim the same title hash to the same slug. A missing
    claim gets its own distinct slug ("none") so a no-title verification
    can't short-circuit a later call that supplies a title — that was the
    hole the audit flagged (30-day "verified" for a URL even when a
    mismatched title was later asserted against it).
    """
    if not claimed_title:
        return "none"
    norm = " ".join(claimed_title.lower().split())
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def get_cache_path(
    url: str,
    cache_dir: Path,
    claimed_title: str | None = None,
) -> Path:
    """Return cache file path for (url, claimed_title).

    Keying by (url, claimed_title) closes the bug where one earlier
    no-title verification could make a URL look "verified" for 30 days
    even when a later call supplied a mismatched title.
    """
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    title_slug = _title_cache_slug(claimed_title)
    return cache_dir / f"{url_hash}.{title_slug}.json"


def _parse_iso_ts(ts: str) -> datetime | None:
    """Parse a timestamp that may be ISO-8601 with offset, with a trailing
    'Z', or missing timezone. Returns None on failure."""
    if not ts:
        return None
    # Normalize legacy 'Z' (pre-3.11 fromisoformat fails on Z).
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_cache(cache_path: Path) -> dict | None:
    """Load cache if fresh (< 30 days). Return None if missing/stale."""
    if not cache_path.exists():
        return None
    try:
        with open(cache_path) as f:
            cached = json.load(f)
    except Exception:
        return None
    fetched = _parse_iso_ts(cached.get("fetched_at", ""))
    if fetched is None:
        return None
    if datetime.now(timezone.utc) - fetched < timedelta(days=30):
        cached["cached"] = True
        return cached
    return None


def save_cache(cache_path: Path, result: dict) -> None:
    """Save result to cache — dense JSON, no whitespace."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_path, "w") as f:
            json.dump(result, f, separators=(",", ":"))
    except Exception:
        pass


def _slim(result: dict) -> dict:
    """Return the minimum downstream-useful subset of a verify result."""
    out = {"url": result["url"], "verified": result["verified"]}
    if not result["verified"] and result.get("reason"):
        out["reason"] = result["reason"]
    return out


def _batch_timeout_result(url: str) -> dict:
    """Return a failure record for a batch worker that exceeded its budget."""
    return {
        "url": url,
        "verified": False,
        "status_code": None,
        "title": "",
        "domain": normalize_domain(url),
        "allowlist_match": False,
        "title_match_score": 0.0,
        "reason": f"verification timed out after {BATCH_RESULT_TIMEOUT_SECONDS}s",
        "cached": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _batch_worker_failure_result(url: str, message: str) -> dict:
    """Return a failure record for a crashed or malformed batch worker."""
    reason = (message or "").strip() or "verification worker failed"
    return {
        "url": url,
        "verified": False,
        "status_code": None,
        "title": "",
        "domain": normalize_domain(url),
        "allowlist_match": False,
        "title_match_score": 0.0,
        "reason": f"verification worker failed: {reason}",
        "cached": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _single_verify_command(
    url: str,
    claimed_title: str | None = None,
    cache_dir: Path | None = None,
    *,
    verbose: bool = False,
) -> list[str]:
    """Build the child-process command for a single verification."""
    cmd = [sys.executable, str(Path(__file__).resolve()), url]
    if claimed_title:
        cmd.extend(["--claimed-title", claimed_title])
    if cache_dir is not None:
        cmd.extend(["--cache-dir", str(cache_dir)])
    if verbose:
        cmd.append("--verbose")
    return cmd


def _run_batch_subprocesses(
    entries: list[tuple[str, str | None]],
    cache_dir: Path | None = None,
    *,
    verbose: bool = False,
    timeout_seconds: float = BATCH_RESULT_TIMEOUT_SECONDS,
    max_workers: int = BATCH_MAX_WORKERS,
    poll_interval_seconds: float = BATCH_POLL_INTERVAL_SECONDS,
) -> list[dict]:
    """Run batch verification in child processes with real, killable timeouts."""
    results: list[dict | None] = [None] * len(entries)
    pending = list(enumerate(entries))
    running: list[dict] = []

    while pending or running:
        while pending and len(running) < max_workers:
            idx, (url, claimed_title) = pending.pop(0)
            proc = subprocess.Popen(
                _single_verify_command(
                    url,
                    claimed_title,
                    cache_dir,
                    verbose=verbose,
                ),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            running.append(
                {
                    "idx": idx,
                    "url": url,
                    "proc": proc,
                    "started_at": time.monotonic(),
                }
            )

        now = time.monotonic()
        still_running: list[dict] = []
        made_progress = False
        for item in running:
            idx = item["idx"]
            url = item["url"]
            proc = item["proc"]
            retcode = proc.poll()
            timed_out = (now - item["started_at"]) >= timeout_seconds

            if retcode is None and not timed_out:
                still_running.append(item)
                continue

            made_progress = True
            if retcode is None:
                proc.kill()
                proc.communicate()
                results[idx] = _batch_timeout_result(url)
                continue

            stdout, stderr = proc.communicate()
            payload = (stdout or "").strip()
            if retcode != 0:
                results[idx] = _batch_worker_failure_result(url, stderr or payload)
                continue
            if not payload:
                results[idx] = _batch_worker_failure_result(
                    url, "worker produced no stdout"
                )
                continue
            try:
                results[idx] = json.loads(payload)
            except json.JSONDecodeError as exc:
                results[idx] = _batch_worker_failure_result(
                    url, f"invalid worker JSON: {exc}"
                )

        running = still_running
        if running and not made_progress:
            time.sleep(poll_interval_seconds)

    return [result for result in results if result is not None]


def verify_url(url: str, claimed_title: str | None = None, cache_dir: Path | None = None) -> dict:
    """Verify a single URL.

    The cache key includes ``claimed_title`` so a previous no-title
    verification cannot "approve" a later call that supplies a title. The
    legacy single-hash cache path is still checked as a read-through
    fallback — but ONLY when no claim is being made now (i.e. it can't
    short-circuit a title check that never happened).
    """
    if cache_dir is None:
        override = os.environ.get("LESSON_PLAN_MAGIC_HOME")
        home_root = (
            Path(override).expanduser()
            if override
            else Path.home() / "Documents" / "Lesson Plan Magic"
        )
        cache_dir = home_root / ".cache" / "verify"

    cache_path = get_cache_path(url, cache_dir, claimed_title)
    cached = load_cache(cache_path)
    if cached:
        return cached

    # Legacy cache (pre-0.2.2) was keyed by URL only. Honor a hit ONLY
    # when the current call has no claimed_title — otherwise the old
    # record can't prove the title was ever checked and we must refetch.
    if claimed_title is None:
        legacy_path = get_cache_path(url, cache_dir, None)
        # Different file name when claimed_title is None → same as cache_path;
        # fall back to the true URL-only hash for pre-0.2.2 caches.
        legacy_url_only = cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
        if legacy_url_only != cache_path:
            legacy_cached = load_cache(legacy_url_only)
            if legacy_cached:
                return legacy_cached

    domain = normalize_domain(url)
    now = datetime.now(timezone.utc).isoformat()

    if is_blocklisted(domain):
        result = {
            "url": url,
            "verified": False,
            "status_code": None,
            "title": "",
            "domain": domain,
            "allowlist_match": False,
            "title_match_score": 0.0,
            "reason": "domain is blocklisted",
            "cached": False,
            "fetched_at": now,
        }
        save_cache(cache_path, result)
        return result

    allowlist_match = matches_allowlist(domain)
    conditional_match = requires_title_match(domain)
    status_code, title = fetch_title(url)

    if status_code != 200:
        reason = (
            title
            if status_code in (0, None) and title
            else f"HTTP {status_code}"
        )
        result = {
            "url": url,
            "verified": False,
            "status_code": status_code,
            "title": title,
            "domain": domain,
            "allowlist_match": allowlist_match,
            "title_match_score": 0.0,
            "reason": reason,
            "cached": False,
            "fetched_at": now,
        }
        save_cache(cache_path, result)
        return result

    title_match_score = 0.0
    if claimed_title:
        title_match_score = fuzzy_title_match(claimed_title, title)

    # Verification logic: allowlisted domains still require a title match
    # when a claimed_title is provided, to avoid marking stale/wrong pages
    # as "verified" just because they sit on a trusted domain.
    if conditional_match:
        verified = bool(claimed_title) and _strict_conditional_title_match(
            claimed_title,
            title,
        )
        if not claimed_title:
            reason = "domain requires title match, but no title was claimed"
        elif verified:
            reason = (
                f"conditionally trusted domain + strict title match "
                f"(score {title_match_score:.2f})"
            )
        else:
            reason = (
                f"conditionally trusted domain but title mismatch "
                f"(score {title_match_score:.2f})"
            )
    elif allowlist_match and claimed_title:
        # Trusted domain + title provided → require title match (relaxed threshold)
        verified = title_match_score >= ALLOWLIST_TITLE_MATCH_THRESHOLD
        if verified:
            reason = f"allowlisted domain + title match (score {title_match_score:.2f})"
        else:
            reason = f"allowlisted domain but title mismatch (score {title_match_score:.2f})"
    elif allowlist_match and not claimed_title:
        # Trusted domain, no title to check → verified (backward-compatible)
        verified = True
        reason = "allowlisted domain (no title claim to check)"
    elif claimed_title and title_match_score >= NON_ALLOWLIST_TITLE_MATCH_THRESHOLD:
        # Not allowlisted, but title matches well → verified
        verified = True
        reason = f"title match (score {title_match_score:.2f})"
    else:
        verified = False
        reason = "domain not allowlisted and no title match"

    result = {
        "url": url,
        "verified": verified,
        "status_code": status_code,
        "title": title,
        "domain": domain,
        "allowlist_match": allowlist_match,
        "title_match_score": title_match_score,
        "reason": reason,
        "cached": False,
        "fetched_at": now,
    }
    save_cache(cache_path, result)
    return result


def _parse_batch_line(line: str) -> tuple[str, str | None] | None:
    """Parse one line of a batch file.

    Accepted forms (per SKILL.md Step 5):
      * JSON object: ``{"url": "...", "claimed_title": "...", ...}``
        Extra fields like ``why_relevant`` are ignored.
      * JSON-Lines alias: ``{"url": "...", "title": "..."}`` also accepted.
      * Raw URL: ``https://example.com/foo`` (backward-compatible, no title)

    Blank lines and ``#`` comments return None.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("{"):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return None
        url = obj.get("url")
        if not isinstance(url, str) or not url:
            return None
        claimed = obj.get("claimed_title") or obj.get("title")
        if claimed is not None and not isinstance(claimed, str):
            claimed = str(claimed)
        return url, (claimed or None)
    # Raw URL fallback
    return line, None


def main() -> int:
    """CLI entry point. Stdout is slim by default (--verbose = full record)."""
    if len(sys.argv) < 2:
        print(
            "Usage: verify_research.py <url> [--claimed-title \"Title\"] "
            "[--cache-dir PATH] [--verbose]",
            file=sys.stderr,
        )
        print(
            "       verify_research.py --batch candidates.jsonl "
            "[--cache-dir PATH] [--verbose]",
            file=sys.stderr,
        )
        print(
            "  Batch file: one JSON object per line with at minimum "
            "'url' and optional 'claimed_title'. Raw URL lines are "
            "accepted for backward compatibility (no title match).",
            file=sys.stderr,
        )
        return 1

    cache_dir = None
    if "--cache-dir" in sys.argv:
        idx = sys.argv.index("--cache-dir")
        if idx + 1 < len(sys.argv):
            cache_dir = Path(sys.argv[idx + 1]).expanduser()

    verbose = "--verbose" in sys.argv
    emit = (lambda r: r) if verbose else _slim

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Error: --batch requires a file path", file=sys.stderr)
            return 1
        batch_file = sys.argv[2]
        try:
            with open(batch_file) as f:
                lines = list(f)
        except Exception as e:
            print(f"Error reading batch file: {e}", file=sys.stderr)
            return 1

        entries: list[tuple[str, str | None]] = []
        for raw in lines:
            parsed = _parse_batch_line(raw)
            if parsed is not None:
                entries.append(parsed)

        results = _run_batch_subprocesses(
            entries,
            cache_dir,
            verbose=verbose,
        )
        for result in results:
            print(json.dumps(emit(result), separators=(",", ":")))
        return 0
    else:
        url = sys.argv[1]
        claimed_title = None
        if "--claimed-title" in sys.argv:
            idx = sys.argv.index("--claimed-title")
            if idx + 1 < len(sys.argv):
                claimed_title = sys.argv[idx + 1]

        result = verify_url(url, claimed_title, cache_dir)
        print(json.dumps(emit(result), separators=(",", ":")))
        return 0


if __name__ == "__main__":
    sys.exit(main())
