"""Tests for parse_standards.py — framework detection, code extraction,
URL safety, and CLI surface."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document

import parse_standards as ps


SCRIPT_PATH = (
    Path(__file__).parent.parent
    / "skills" / "lesson-planner" / "scripts" / "parse_standards.py"
)


def _validated(url: str):
    return SimpleNamespace(url=url)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

def _build_pdf(path: Path, pages: list[str]) -> None:
    """Write a simple multi-page PDF containing the given page strings."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    for page_text in pages:
        y = height - 72
        for line in page_text.splitlines() or [""]:
            c.drawString(72, y, line)
            y -= 14
        c.showPage()
    c.save()


def _build_docx(path: Path, paragraphs: list[str]) -> None:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc.save(str(path))


# ---------------------------------------------------------------------------
# Framework detection
# ---------------------------------------------------------------------------

class TestDetectFramework:
    @pytest.mark.parametrize("text,expected", [
        ("Next Generation Science Standards — Physical Sciences", "NGSS"),
        ("This packet references NGSS DCIs.", "NGSS"),
        ("Common Core State Standards for English Language Arts, Grade 9",
         "Common Core ELA"),
        ("CCSS.ELA-LITERACY reference doc", "Common Core ELA"),
        ("Common Core State Standards for Mathematics — Algebra 1",
         "Common Core Math"),
        ("Georgia Standards of Excellence", "Georgia Standards of Excellence"),
        ("GSE Physical Science curriculum map",
         "Georgia Standards of Excellence"),
        ("AP Course and Exam Description — US History",
         "AP College Board"),
        ("Texas Essential Knowledge and Skills", "TEKS"),
        ("C3 Framework for Social Studies State Standards",
         "C3 Social Studies"),
    ])
    def test_known_frameworks(self, text, expected):
        assert ps.detect_framework(text) == expected

    def test_unknown_framework(self):
        assert ps.detect_framework("random marketing copy") == "unknown"

    def test_case_insensitive(self):
        assert ps.detect_framework("next generation science standards") == "NGSS"

    def test_first_match_in_head(self):
        """Detection only scans the first 10k chars; a tag past that window is missed."""
        far = ("padding " * 2000) + " Next Generation Science Standards"
        assert ps.detect_framework(far) == "unknown"

        near = ("padding " * 100) + " Next Generation Science Standards"
        assert ps.detect_framework(near) == "NGSS"


# ---------------------------------------------------------------------------
# Grade-level detection
# ---------------------------------------------------------------------------

class TestDetectGradeLevels:
    def test_grade_range(self):
        assert ps.detect_grade_levels("Grades 6-8") == ["6", "7", "8"]

    def test_en_dash_range(self):
        assert ps.detect_grade_levels("Grades 6\u20138") == ["6", "7", "8"]

    def test_kindergarten(self):
        assert "K" in ps.detect_grade_levels("Grade K activities")

    def test_band_aliases(self):
        out = ps.detect_grade_levels("High School physics course")
        assert "9-12" in out

    def test_multiple_bands_deduped(self):
        out = ps.detect_grade_levels(
            "Grade 9 through Grade 12. This is a High School course."
        )
        assert "9" in out and "12" in out and "9-12" in out

    def test_no_grade_info(self):
        assert ps.detect_grade_levels("standalone tutorial") == []


# ---------------------------------------------------------------------------
# Standard extraction
# ---------------------------------------------------------------------------

class TestExtractStandardsNGSS:
    def test_extracts_ngss_codes(self):
        text = (
            "HS-PS1-1. Students use the periodic table to predict bonding.\n"
            "HS-PS1-2. Students construct explanations of chemical reactions."
        )
        out = ps.extract_standards(text, "NGSS")
        codes = [s.code for s in out]
        assert codes == ["HS-PS1-1", "HS-PS1-2"]

    def test_dedupes_ngss_codes(self):
        text = "HS-PS1-1. First mention.\nLater, HS-PS1-1 again."
        out = ps.extract_standards(text, "NGSS")
        assert len(out) == 1

    def test_populates_short_and_full_text(self):
        text = "MS-LS1-1. Students construct an argument. " + ("x" * 500)
        out = ps.extract_standards(text, "NGSS")
        assert len(out[0].short_text) <= 200
        assert len(out[0].full_text) <= 800


class TestExtractStandardsCCELA:
    def test_ela_code_shape(self):
        text = "CCSS.ELA-LITERACY.RL.9.1: Cite textual evidence."
        out = ps.extract_standards(text, "Common Core ELA")
        assert out and out[0].code == "CCSS.ELA-LITERACY.RL.9.1"


class TestExtractStandardsPageMap:
    def test_source_page_assigned(self):
        text = "Intro\n\n" + "padding " * 50 + "\n\nHS-PS1-1. ..."
        # Page-map: page 1 starts at 0, page 2 starts at 100 (somewhere before code).
        pm = {1: 0, 2: 50}
        out = ps.extract_standards(text, "NGSS", page_map=pm)
        assert out and out[0].source_page is not None


class TestExtractStandardsGeneric:
    def test_generic_line_fallback(self):
        text = (
            "SCI-301  Explain Newton's third law.\n"
            "SCI-302  Apply conservation of momentum.\n"
        )
        # Unknown framework: falls through to GENERIC_CODE linewise.
        out = ps.extract_standards(text, "unknown-framework")
        codes = [s.code for s in out]
        assert "SCI-301" in codes and "SCI-302" in codes


# ---------------------------------------------------------------------------
# parse_pdf / parse_docx / parse_text
# ---------------------------------------------------------------------------

class TestParsePdf:
    def test_roundtrip(self, tmp_path):
        pdf_path = tmp_path / "ngss.pdf"
        _build_pdf(pdf_path, [
            "Next Generation Science Standards\nGrades 6-8",
            "MS-LS1-1. Students construct an argument.\n"
            "MS-LS1-2. Students develop a model.",
        ])
        result = ps.parse_pdf(pdf_path)
        assert result.framework == "NGSS"
        assert result.source.type == "pdf"
        assert result.source.hash and result.source.hash.startswith("sha256:")
        codes = [s.code for s in result.standards]
        assert "MS-LS1-1" in codes and "MS-LS1-2" in codes


class TestParseDocx:
    def test_docx_framework_and_codes(self, tmp_path):
        path = tmp_path / "standards.docx"
        _build_docx(path, [
            "Common Core State Standards for English Language Arts",
            "CCSS.ELA-LITERACY.RL.9.1: Cite textual evidence.",
            "CCSS.ELA-LITERACY.RL.9.2: Determine a theme.",
        ])
        result = ps.parse_docx(path)
        assert result.framework == "Common Core ELA"
        assert result.source.type == "docx"
        codes = [s.code for s in result.standards]
        assert "CCSS.ELA-LITERACY.RL.9.1" in codes


class TestParseText:
    def test_text_framework_and_codes(self):
        text = (
            "Next Generation Science Standards\n"
            "HS-PS1-1. Use the periodic table."
        )
        result = ps.parse_text(text)
        assert result.framework == "NGSS"
        assert result.source.type == "text"
        assert result.standards[0].code == "HS-PS1-1"


# ---------------------------------------------------------------------------
# Dense serializer
# ---------------------------------------------------------------------------

class TestDenseSerializer:
    def test_short_keys_and_null_drop(self):
        pt = ps.parse_text("NGSS\nHS-PS1-1. description here.")
        dense = ps._to_dense(pt)
        assert "s" in dense and "f" in dense and "g" in dense and "S" in dense
        assert "t" in dense["s"]
        assert "h" in dense["s"]  # hash always present
        # URL/path should be dropped on text sources.
        assert "p" not in dense["s"]
        assert "u" not in dense["s"]
        std = dense["S"][0]
        assert "c" in std and "st" in std
        # Full-text dropped when equal to short.

    def test_full_dict_has_long_keys(self):
        pt = ps.parse_text("NGSS\nHS-PS1-1. description.")
        full = ps._to_dict(pt)
        assert set(full) == {"source", "framework", "grade_levels", "standards"}


# ---------------------------------------------------------------------------
# URL validation — SSRF guard
# ---------------------------------------------------------------------------

class TestValidateUrl:
    def test_rejects_file_scheme(self):
        with pytest.raises(ValueError):
            ps._validate_url("file:///etc/passwd")

    def test_rejects_gopher_scheme(self):
        with pytest.raises(ValueError):
            ps._validate_url("gopher://example.com/resource")

    def test_rejects_data_scheme(self):
        with pytest.raises(ValueError):
            ps._validate_url("data:text/plain;base64,QUJD")

    def test_rejects_missing_hostname(self):
        with pytest.raises(ValueError):
            ps._validate_url("http:///path")

    def test_rejects_loopback(self):
        with pytest.raises(ValueError):
            ps._validate_url("http://127.0.0.1/x")

    def test_rejects_private_rfc1918(self):
        with pytest.raises(ValueError):
            ps._validate_url("http://10.0.0.1/x")

    def test_rejects_link_local(self):
        with pytest.raises(ValueError):
            ps._validate_url("http://169.254.169.254/")


# ---------------------------------------------------------------------------
# parse_url — mocked HTTP
# ---------------------------------------------------------------------------

class TestParseUrl:
    def test_html_fetch_parses_framework(self, monkeypatch):
        seen = {}

        monkeypatch.setattr(ps, "_validate_url", lambda url: _validated(url))
        def fake_fetch(url, **kwargs):
            seen.update(kwargs)
            return (
                200,
                {"Content-Type": "text/html"},
                (
                    "<html><body>Next Generation Science Standards"
                    "<p>HS-PS1-1 description.</p></body></html>"
                ).encode("utf-8"),
            )

        monkeypatch.setattr(ps.safe_http, "fetch_url", fake_fetch)
        result = ps.parse_url("https://example.gov/ngss.html")
        assert result.framework == "NGSS"
        assert result.source.type == "url"
        assert result.source.url == "https://example.gov/ngss.html"
        assert result.source.hash.startswith("sha256:")
        assert seen["max_body_bytes"] == ps.MAX_FETCH_BYTES

    def test_http_error_raises(self, monkeypatch):
        monkeypatch.setattr(ps, "_validate_url", lambda url: _validated(url))
        monkeypatch.setattr(
            ps.safe_http,
            "fetch_url",
            lambda url, **kwargs: (404, {"Content-Type": "text/html"}, b""),
        )
        with pytest.raises(Exception):
            ps.parse_url("https://example.gov/missing")

    def test_rejects_file_url(self):
        with pytest.raises(ValueError):
            ps.parse_url("file:///etc/passwd")

    def test_rejects_loopback_url(self):
        with pytest.raises(ValueError):
            ps.parse_url("http://localhost/anything")

    def test_redirect_to_private_ip_blocked(self, monkeypatch):
        seen = []

        def fake_validate(url):
            seen.append(url)
            if url == "http://10.0.0.1/internal":
                raise ValueError("Blocked private/loopback target: 10.0.0.1")
            return _validated(url)

        monkeypatch.setattr(ps, "_validate_url", fake_validate)
        monkeypatch.setattr(
            ps.safe_http,
            "fetch_url",
            lambda url, **kwargs: (
                302,
                {"Location": "http://10.0.0.1/internal"},
                b"",
            ),
        )
        with pytest.raises(ValueError):
            ps.parse_url("https://example.gov/start")
        assert seen == [
            "https://example.gov/start",
            "http://10.0.0.1/internal",
        ]

    def test_parse_url_closes_mkstemp_fd(self, monkeypatch, tmp_path):
        closed = []
        temp_path = tmp_path / "download.html"

        monkeypatch.setattr(ps, "_validate_url", lambda url: _validated(url))
        monkeypatch.setattr(
            ps.safe_http,
            "fetch_url",
            lambda url, **kwargs: (
                200,
                {"Content-Type": "text/html"},
                b"<html><body>Next Generation Science Standards"
                b"<p>HS-PS1-1 description.</p></body></html>",
            ),
        )
        monkeypatch.setattr(
            ps.tempfile,
            "mkstemp",
            lambda suffix: (123, str(temp_path)),
        )
        monkeypatch.setattr(ps.os, "close", lambda fd: closed.append(fd))

        result = ps.parse_url("https://example.gov/ngss.html")

        assert result.framework == "NGSS"
        assert closed == [123]
        assert not temp_path.exists()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class TestCli:
    def test_stdin_pipe(self):
        text = "Next Generation Science Standards\nHS-PS1-1. description."
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--stdin", "--pretty"],
            input=text, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["framework"] == "NGSS"
        assert data["standards"][0]["code"] == "HS-PS1-1"

    def test_cli_missing_file(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--input", str(tmp_path / "does_not_exist.pdf")],
            capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_cli_unsupported_extension(self, tmp_path):
        f = tmp_path / "data.xlsx"
        f.write_text("not used")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(f)],
            capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "unsupported" in result.stderr.lower()

    def test_cli_cache_write(self, tmp_path):
        text_file = tmp_path / "in.md"
        text_file.write_text("NGSS\nHS-PS1-1. desc.")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--input", str(text_file),
             "--subject", "chem",
             "--cache-dir", str(tmp_path / "cache")],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        cache = tmp_path / "cache" / "chem.parsed.json"
        assert cache.exists()
        data = json.loads(cache.read_text())
        # Dense format uses short keys.
        assert "s" in data and "S" in data

    def test_cli_rejects_non_kebab_subject_id_for_cache_write(self, tmp_path):
        text_file = tmp_path / "in.md"
        text_file.write_text("NGSS\nHS-PS1-1. desc.")
        cache_dir = tmp_path / "cache"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--input",
                str(text_file),
                "--subject",
                "../escaped",
                "--cache-dir",
                str(cache_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "subject id must be kebab-case" in result.stderr.lower()
        assert not (tmp_path / "escaped.parsed.json").exists()
        assert not cache_dir.exists()
