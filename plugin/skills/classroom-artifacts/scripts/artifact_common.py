#!/usr/bin/env python3
"""Shared safety helpers for classroom-artifacts scripts."""

from __future__ import annotations

import os
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised through CLI error path
    yaml = None


MAX_CONFIG_BYTES = 1 * 1024 * 1024


def _home_root() -> Path:
    # Override with LESSON_PLAN_MAGIC_HOME for managed installs (e.g. Windows
    # profiles where Documents is redirected) or non-standard layouts.
    override = os.environ.get("LESSON_PLAN_MAGIC_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / "Documents" / "Lesson Plan Magic"


DEFAULT_CONFIG_PATH = _home_root() / "config.yaml"
DEFAULT_OUTPUT_DIR = _home_root() / "outputs"


def default_output_dir() -> Path:
    return DEFAULT_OUTPUT_DIR.resolve()


def resolve_output_path(output_arg: str, *, allow_anywhere: bool = False) -> Path:
    """Resolve an output path and fence it to the documented outputs dir."""
    resolved = Path(output_arg).expanduser().resolve()
    if allow_anywhere:
        return resolved

    output_root = default_output_dir()
    try:
        resolved.relative_to(output_root)
    except ValueError as exc:
        raise ValueError(
            f"Output path must stay within {output_root} unless --allow-anywhere is passed."
        ) from exc
    return resolved


def load_config(config_arg: str | None) -> dict:
    """Load config YAML and fail closed on malformed or unreadable files."""
    path = Path(config_arg).expanduser() if config_arg else DEFAULT_CONFIG_PATH
    if not path.exists():
        if config_arg:
            raise FileNotFoundError(f"Config file not found: {path}")
        return {}

    if yaml is None:
        raise RuntimeError("pyyaml is required to load config files.")

    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Could not stat config file: {exc}") from exc
    if size > MAX_CONFIG_BYTES:
        raise ValueError(
            f"Config file exceeds the {MAX_CONFIG_BYTES}-byte limit: {path}"
        )

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Could not load config: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("Config file must decode to a YAML mapping.")
    return data
