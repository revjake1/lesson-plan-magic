"""Tests for runtime bootstrap messaging."""

from pathlib import Path

import pytest

import runtime_bootstrap as rb


def test_bootstrap_failure_message_lists_requirements(monkeypatch, tmp_path):
    monkeypatch.setenv("LESSON_PLAN_MAGIC_HOME", str(tmp_path / "Lesson Plan Magic"))

    with pytest.raises(SystemExit) as excinfo:
        rb.ensure_plugin_runtime_or_exit(Path("/missing/plugin-anchor.py"))

    assert excinfo.value.code == 1


def test_bootstrap_failure_message_text_includes_next_steps(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("LESSON_PLAN_MAGIC_HOME", str(tmp_path / "Lesson Plan Magic"))

    with pytest.raises(SystemExit):
        rb.ensure_plugin_runtime_or_exit(Path("/missing/plugin-anchor.py"))

    stderr = capsys.readouterr().err
    assert "Python 3.9 or newer" in stderr
    assert "https://python.org" in stderr
    assert "retry the helper install automatically" in stderr
