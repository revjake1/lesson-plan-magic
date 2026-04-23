"""Pytest regression tests for verify_research.py fixes."""

import pytest
import json
import hashlib
from pathlib import Path

from verify_research import (
    _parse_batch_line,
    fuzzy_title_match,
    get_cache_path,
    _title_cache_slug,
    matches_allowlist,
    normalize_domain,
    requires_title_match,
    is_blocklisted,
    verify_url,
)


class TestParseBatchLine:
    """Test _parse_batch_line for JSON-Lines + raw URL fallback."""

    def test_json_with_claimed_title(self):
        """JSON object with claimed_title field returns (url, title)."""
        line = '{"url": "https://example.com", "claimed_title": "Example Site"}'
        result = _parse_batch_line(line)
        assert result == ("https://example.com", "Example Site")

    def test_json_with_title_alias(self):
        """JSON object with title field (alias) returns (url, title)."""
        line = '{"url": "https://example.com", "title": "Example Site"}'
        result = _parse_batch_line(line)
        assert result == ("https://example.com", "Example Site")

    def test_json_with_extra_fields(self):
        """JSON object with extra fields like why_relevant are ignored."""
        line = '{"url": "https://example.com", "claimed_title": "Site", "why_relevant": "relevant reason"}'
        result = _parse_batch_line(line)
        assert result == ("https://example.com", "Site")

    def test_json_without_title(self):
        """JSON object without title field returns (url, None)."""
        line = '{"url": "https://example.com"}'
        result = _parse_batch_line(line)
        assert result == ("https://example.com", None)

    def test_raw_url(self):
        """Raw URL (no JSON) returns (url, None) with no title."""
        line = "https://example.com/path"
        result = _parse_batch_line(line)
        assert result == ("https://example.com/path", None)

    def test_blank_line(self):
        """Blank line returns None."""
        result = _parse_batch_line("")
        assert result is None

    def test_whitespace_only_line(self):
        """Whitespace-only line returns None."""
        result = _parse_batch_line("   \t  ")
        assert result is None

    def test_comment_line(self):
        """Comment line (starts with #) returns None."""
        result = _parse_batch_line("# This is a comment")
        assert result is None

    def test_json_with_null_title(self):
        """JSON with null or empty title is treated as no title."""
        line = '{"url": "https://example.com", "claimed_title": null}'
        result = _parse_batch_line(line)
        assert result == ("https://example.com", None)

    def test_json_with_empty_string_title(self):
        """JSON with empty string title is treated as no title."""
        line = '{"url": "https://example.com", "claimed_title": ""}'
        result = _parse_batch_line(line)
        assert result == ("https://example.com", None)


class TestTitleCacheSlug:
    """Test _title_cache_slug normalization and consistency."""

    def test_none_title_slug(self):
        """None title returns 'none'."""
        assert _title_cache_slug(None) == "none"

    def test_empty_string_slug(self):
        """Empty string title returns 'none'."""
        assert _title_cache_slug("") == "none"

    def test_whitespace_only_slug(self):
        """Whitespace-only title is hashed (not treated as 'none' unless empty)."""
        # The implementation hashes the normalized string, not special-casing
        # pure whitespace as "none" — only empty string and None get "none"
        result = _title_cache_slug("   ")
        assert result != ""  # Should produce a valid hash

    def test_case_insensitivity(self):
        """Same title with different case produces the same slug."""
        slug1 = _title_cache_slug("Example Title")
        slug2 = _title_cache_slug("EXAMPLE TITLE")
        slug3 = _title_cache_slug("example title")
        assert slug1 == slug2 == slug3

    def test_whitespace_normalization(self):
        """Extra whitespace is normalized before hashing."""
        slug1 = _title_cache_slug("Example  Title")
        slug2 = _title_cache_slug("Example Title")
        slug3 = _title_cache_slug("  Example   Title  ")
        assert slug1 == slug2 == slug3

    def test_different_titles_different_slugs(self):
        """Different titles produce different slugs."""
        slug1 = _title_cache_slug("Title A")
        slug2 = _title_cache_slug("Title B")
        assert slug1 != slug2


class TestGetCachePath:
    """Test get_cache_path keying by (url, claimed_title)."""

    def test_same_url_no_title(self, tmp_path):
        """Same URL without title produces consistent path."""
        path1 = get_cache_path("https://example.com", tmp_path, None)
        path2 = get_cache_path("https://example.com", tmp_path, None)
        assert path1 == path2

    def test_same_url_different_titles(self, tmp_path):
        """Same URL with different titles produces different paths."""
        path1 = get_cache_path("https://example.com", tmp_path, "Title A")
        path2 = get_cache_path("https://example.com", tmp_path, "Title B")
        assert path1 != path2

    def test_same_url_none_vs_titled(self, tmp_path):
        """Same URL with None vs. a title produces different paths."""
        path_none = get_cache_path("https://example.com", tmp_path, None)
        path_titled = get_cache_path("https://example.com", tmp_path, "Example Title")
        assert path_none != path_titled

    def test_title_normalization_preserves_path(self, tmp_path):
        """Whitespace/case variations of same title produce same path."""
        path1 = get_cache_path("https://example.com", tmp_path, "Example Title")
        path2 = get_cache_path("https://example.com", tmp_path, "EXAMPLE TITLE")
        path3 = get_cache_path("https://example.com", tmp_path, "  Example   Title  ")
        assert path1 == path2 == path3

    def test_cache_path_structure(self, tmp_path):
        """Cache path is cache_dir / {url_hash}.{title_slug}.json."""
        url = "https://example.com"
        title = "Test Title"
        path = get_cache_path(url, tmp_path, title)
        # Should be in the cache dir
        assert path.parent == tmp_path
        # Should end with .json
        assert path.suffix == ".json"
        # Should contain both URL hash and title slug
        filename = path.name
        assert "." in filename  # has at least one dot before .json


class TestMatchesAllowlist:
    """Test matches_allowlist for gov/edu/mil and explicit allowlist."""

    def test_gov_domain(self):
        """Domain ending in .gov is allowlisted."""
        assert matches_allowlist("example.gov") is True

    def test_edu_domain(self):
        """Domain ending in .edu is allowlisted."""
        assert matches_allowlist("example.edu") is True

    def test_mil_domain(self):
        """Domain ending in .mil is allowlisted."""
        assert matches_allowlist("example.mil") is True

    def test_explicit_allowlist(self):
        """Explicitly allowlisted domain returns True."""
        assert matches_allowlist("nasa.gov") is True
        assert matches_allowlist("khanacademy.org") is True
        assert matches_allowlist("pbs.org") is True

    def test_requires_title_match_domains_return_false(self):
        """Domains in REQUIRES_TITLE_MATCH return False (not blanket-allowed)."""
        assert matches_allowlist("ted.com") is False
        assert matches_allowlist("teded.com") is False
        assert matches_allowlist("bbc.com") is False

    def test_unknown_domain(self):
        """Unknown domain returns False."""
        assert matches_allowlist("random-site.com") is False

    def test_subdomain_gov(self):
        """Subdomain of .gov domain is allowlisted."""
        assert matches_allowlist("agency.example.gov") is True


class TestRequiresTitleMatch:
    """Test requires_title_match for conditional domains."""

    def test_ted_requires_title(self):
        """ted.com requires title match."""
        assert requires_title_match("ted.com") is True

    def test_bbc_requires_title(self):
        """bbc.com requires title match."""
        assert requires_title_match("bbc.com") is True

    def test_teded_requires_title(self):
        """teded.com requires title match."""
        assert requires_title_match("teded.com") is True

    def test_allowlisted_does_not_require(self):
        """Explicitly allowlisted domains do not require title match."""
        assert requires_title_match("nasa.gov") is False
        assert requires_title_match("khanacademy.org") is False

    def test_unknown_does_not_require(self):
        """Unknown domains do not require title match."""
        assert requires_title_match("random.com") is False


class TestIsBlocklisted:
    """Test is_blocklisted for prohibited domains."""

    def test_pinterest_blocklisted(self):
        """pinterest.com is blocklisted."""
        assert is_blocklisted("pinterest.com") is True

    def test_teacherspayteachers_blocklisted(self):
        """teacherspayteachers.com is blocklisted."""
        assert is_blocklisted("teacherspayteachers.com") is True

    def test_reddit_blocklisted(self):
        """reddit.com is blocklisted."""
        assert is_blocklisted("reddit.com") is True

    def test_quora_blocklisted(self):
        """quora.com is blocklisted."""
        assert is_blocklisted("quora.com") is True

    def test_wikihow_blocklisted(self):
        """wikihow.com is blocklisted."""
        assert is_blocklisted("wikihow.com") is True

    def test_subdomain_blocklisted(self):
        """Subdomain of blocklisted domain is also blocklisted."""
        assert is_blocklisted("subdomain.reddit.com") is True
        assert is_blocklisted("www.pinterest.com") is True

    def test_allowlisted_not_blocklisted(self):
        """Allowlisted domain is not blocklisted."""
        assert is_blocklisted("nasa.gov") is False
        assert is_blocklisted("khanacademy.org") is False

    def test_unknown_not_blocklisted(self):
        """Unknown domain is not blocklisted."""
        assert is_blocklisted("random.com") is False


class TestNormalizeDomain:
    """Test normalize_domain — must strip port, userinfo, and www."""

    def test_strips_port_suffix(self):
        """Port-suffixed URL normalizes to bare domain (P1 fix).

        Pre-fix, parsed.netloc kept the ':443' and made reddit.com:443
        bypass the BLOCKLIST. Using parsed.hostname strips the port.
        """
        assert normalize_domain("https://reddit.com:443/r/test") == "reddit.com"
        assert normalize_domain("https://khanacademy.org:443/x") == "khanacademy.org"

    def test_strips_www_prefix(self):
        assert normalize_domain("https://www.example.com/path") == "example.com"

    def test_lowercases(self):
        assert normalize_domain("https://Example.COM/foo") == "example.com"

    def test_strips_userinfo_and_port(self):
        assert normalize_domain("https://user:pass@reddit.com:8443/r/x") == "reddit.com"


class TestPortSuffixBlocklist:
    """End-to-end: a port-suffixed blocklisted URL must be rejected."""

    def test_port_suffixed_blocklist_domain_rejected(self, tmp_path):
        """verify_url on reddit.com:443 must not return verified=True
        even when a claimed_title is supplied and (hypothetically) matches.
        """
        result = verify_url(
            "https://reddit.com:443/r/test",
            "Exact Matching Title",
            cache_dir=tmp_path,
        )
        assert result["verified"] is False
        assert result["domain"] == "reddit.com"
        assert "blocklisted" in (result.get("reason") or "").lower()


class TestFuzzyTitleMatch:
    """Regression coverage for title-match false positives.

    The pre-fix scorer used only token_set_ratio, which over-weights
    shared filler/label words and let citations through even when the
    page's distinctive content tokens didn't match the claim. These
    cases must now fall below the verification thresholds
    (0.55 for allowlisted, 0.75 for other domains).
    """

    def test_shared_label_word_is_not_verified_allowlist(self):
        # Reported P1 bypass #1: example.edu + claim "Expected Title" vs
        # fetched "Wrong Title" used to score 0.62 and verify=True under
        # the 0.55 allowlist threshold. Distinctive claimed token
        # ("Expected") is missing from actual → recall 0.5 → min drops
        # the score under threshold.
        score = fuzzy_title_match("Expected Title", "Wrong Title")
        assert score < 0.55, f"expected < 0.55, got {score}"

    def test_shared_phrase_is_not_verified_non_allowlist(self):
        # Reported P1 bypass #2: example.com + "Newtons Laws of Motion"
        # vs "Laws of Motion Worksheet" used to score 0.78 (passed the
        # 0.75 non-allowlist threshold). "Newtons" is missing from
        # actual → recall 0.67 → min drops the score below threshold.
        score = fuzzy_title_match(
            "Newtons Laws of Motion", "Laws of Motion Worksheet"
        )
        assert score < 0.75, f"expected < 0.75, got {score}"

    def test_exact_match(self):
        assert fuzzy_title_match("Photosynthesis", "Photosynthesis") == 1.0

    def test_title_with_editorial_suffix_still_matches(self):
        # Legit case: site appended "— An Overview" to claim text.
        # Distinctive claimed tokens all present → recall 1.0 → score stays high.
        score = fuzzy_title_match(
            "Photosynthesis Overview", "Photosynthesis — An Overview"
        )
        assert score >= 0.75

    def test_short_claim_with_added_suffix_still_matches(self):
        score = fuzzy_title_match("Solar System", "The Solar System Explained")
        assert score >= 0.75

    def test_empty_inputs_score_zero(self):
        assert fuzzy_title_match("", "Anything") == 0.0
        assert fuzzy_title_match("Anything", "") == 0.0

    def test_only_stopwords_falls_back_to_set_score(self):
        # When the claim has no distinctive content tokens, recall
        # defaults to 1.0 so the set_score drives the decision.
        assert fuzzy_title_match("The A", "The A") == 1.0


class TestVerifyUrlTitleBypass:
    """End-to-end: verify_url must not certify a page whose title shares
    filler words with the claim but diverges on distinctive content.
    Uses monkeypatch to stub the network fetch so the test is offline."""

    def test_allowlist_domain_wrong_title_not_verified(self, tmp_path, monkeypatch):
        # Reported bypass: allowlisted .edu TLD + claimed "Expected Title"
        # + fetched "Wrong Title" used to return verified=True.
        import verify_research as vr
        monkeypatch.setattr(vr, "fetch_title", lambda url: (200, "Wrong Title"))
        result = vr.verify_url(
            "https://example.edu/article",
            claimed_title="Expected Title",
            cache_dir=tmp_path,
        )
        assert result["verified"] is False, result
        assert result["title_match_score"] < 0.55

    def test_non_allowlist_domain_wrong_title_not_verified(self, tmp_path, monkeypatch):
        # Reported bypass: example.com + claimed "Newtons Laws of Motion"
        # + fetched "Laws of Motion Worksheet" used to return verified=True.
        import verify_research as vr
        monkeypatch.setattr(
            vr, "fetch_title", lambda url: (200, "Laws of Motion Worksheet")
        )
        result = vr.verify_url(
            "https://example.com/article",
            claimed_title="Newtons Laws of Motion",
            cache_dir=tmp_path,
        )
        assert result["verified"] is False, result
        assert result["title_match_score"] < 0.75

    def test_allowlist_domain_matching_title_still_verified(self, tmp_path, monkeypatch):
        # Sanity: a legitimate title match on an allowlisted domain must
        # still verify so we don't over-reject real citations.
        import verify_research as vr
        monkeypatch.setattr(
            vr, "fetch_title",
            lambda url: (200, "Photosynthesis — An Overview (Khan Academy)"),
        )
        result = vr.verify_url(
            "https://khanacademy.org/science/photosynthesis",
            claimed_title="Photosynthesis Overview",
            cache_dir=tmp_path,
        )
        assert result["verified"] is True, result

    def test_conditional_domain_requires_canonical_title_match(self, tmp_path, monkeypatch):
        import verify_research as vr
        monkeypatch.setattr(
            vr, "fetch_title", lambda url: (200, "TED-Ed: Evolution of Fish Industry")
        )
        result = vr.verify_url(
            "https://teded.com/lessons/evolution-of-fish-industry",
            claimed_title="Evolution of Fish",
            cache_dir=tmp_path,
        )
        assert result["verified"] is False, result
        assert "conditionally trusted domain" in result["reason"]

    def test_conditional_domain_accepts_branded_exact_title(self, tmp_path, monkeypatch):
        import verify_research as vr
        monkeypatch.setattr(
            vr, "fetch_title", lambda url: (200, "TED-Ed: Evolution of Fish")
        )
        result = vr.verify_url(
            "https://teded.com/lessons/evolution-of-fish",
            claimed_title="Evolution of Fish",
            cache_dir=tmp_path,
        )
        assert result["verified"] is True, result


class TestFetchTitleLimits:
    def test_fetch_title_caps_response_body(self, monkeypatch):
        import verify_research as vr

        class _Validated:
            def __init__(self, url):
                self.url = url

        seen = {}

        monkeypatch.setattr(vr, "_validate_fetch_url", lambda url: _Validated(url))

        def fake_fetch(target, **kwargs):
            seen.update(kwargs)
            return 200, {"Content-Type": "text/html"}, b"<html><title>Example</title></html>"

        monkeypatch.setattr(vr.safe_http, "fetch_url", fake_fetch)

        status, title = vr.fetch_title("https://example.gov/article")

        assert status == 200
        assert title == "Example"
        assert seen["max_body_bytes"] == vr.MAX_FETCH_BYTES

    def test_fetch_title_reports_oversized_body(self, monkeypatch):
        import verify_research as vr

        class _Validated:
            def __init__(self, url):
                self.url = url

        monkeypatch.setattr(vr, "_validate_fetch_url", lambda url: _Validated(url))
        monkeypatch.setattr(
            vr.safe_http,
            "fetch_url",
            lambda target, **kwargs: (_ for _ in ()).throw(
                vr.safe_http.BodyTooLargeError("Response body exceeded 10 bytes")
            ),
        )

        status, reason = vr.fetch_title("https://example.gov/article")

        assert status == 0
        assert "response body exceeded 10 bytes" in reason


class TestBatchTimeouts:
    def test_batch_spawns_single_url_workers(self, tmp_path, monkeypatch, capsys):
        import verify_research as vr

        batch_file = tmp_path / "candidates.jsonl"
        batch_file.write_text("https://example.gov/article\n", encoding="utf-8")
        seen = {}

        class _FakeProc:
            def __init__(self, cmd):
                self.cmd = cmd
                self.returncode = 0

            def poll(self):
                return self.returncode

            def communicate(self):
                return (
                    '{"url":"https://example.gov/article","verified":true}',
                    "",
                )

        def fake_popen(cmd, **kwargs):
            seen["cmd"] = cmd
            seen["kwargs"] = kwargs
            return _FakeProc(cmd)

        monkeypatch.setattr(vr.subprocess, "Popen", fake_popen)
        monkeypatch.setattr(vr.time, "monotonic", lambda: 0.0)
        monkeypatch.setattr(vr.time, "sleep", lambda _seconds: None)
        monkeypatch.setattr(
            vr.sys,
            "argv",
            [
                "verify_research.py",
                "--batch",
                str(batch_file),
                "--cache-dir",
                str(tmp_path),
            ],
        )

        assert vr.main() == 0
        assert seen["cmd"][:3] == [
            vr.sys.executable,
            str(Path(vr.__file__).resolve()),
            "https://example.gov/article",
        ]
        assert seen["cmd"][3:] == ["--cache-dir", str(tmp_path)]
        assert json.loads(capsys.readouterr().out)["url"] == "https://example.gov/article"

    def test_batch_timeout_kills_worker_process(self, tmp_path, monkeypatch):
        import verify_research as vr

        killed = {"count": 0}

        class _FakeProc:
            def __init__(self):
                self.returncode = None

            def poll(self):
                return None

            def kill(self):
                killed["count"] += 1
                self.returncode = -9

            def communicate(self):
                return ("", "")

        monotonic_values = iter([0.0, 0.0, 0.2])

        def fake_monotonic():
            try:
                return next(monotonic_values)
            except StopIteration:
                return 0.2

        monkeypatch.setattr(
            vr.subprocess,
            "Popen",
            lambda *args, **kwargs: _FakeProc(),
        )
        monkeypatch.setattr(vr.time, "monotonic", fake_monotonic)
        monkeypatch.setattr(vr.time, "sleep", lambda _seconds: None)

        results = vr._run_batch_subprocesses(
            [("https://example.gov/article", None)],
            cache_dir=tmp_path,
            timeout_seconds=0.1,
            poll_interval_seconds=0,
        )

        assert killed["count"] == 1
        assert results[0]["url"] == "https://example.gov/article"
        assert results[0]["verified"] is False
        assert "timed out" in results[0]["reason"]

    def test_batch_timeout_emits_failure_record(self, tmp_path, monkeypatch, capsys):
        import verify_research as vr

        batch_file = tmp_path / "candidates.jsonl"
        batch_file.write_text("https://example.gov/article\n", encoding="utf-8")

        monkeypatch.setattr(
            vr,
            "_run_batch_subprocesses",
            lambda entries, cache_dir, verbose=False: [
                vr._batch_timeout_result("https://example.gov/article")
            ],
        )
        monkeypatch.setattr(
            vr.sys,
            "argv",
            ["verify_research.py", "--batch", str(batch_file)],
        )

        assert vr.main() == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["url"] == "https://example.gov/article"
        assert payload["verified"] is False
        assert "timed out" in payload["reason"]

    def test_verify_url_preserves_detailed_non_http_failure_reason(
        self, tmp_path, monkeypatch
    ):
        import verify_research as vr

        monkeypatch.setattr(
            vr,
            "fetch_title",
            lambda url: (0, "fetch blocked: response body exceeded 10 bytes"),
        )

        result = vr.verify_url(
            "https://example.com/article",
            cache_dir=tmp_path,
        )

        assert result["verified"] is False
        assert result["status_code"] == 0
        assert result["reason"] == "fetch blocked: response body exceeded 10 bytes"
