#!/usr/bin/env python3
"""Shared safety helpers for classroom-artifacts scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

_SHARED_DIR = Path(__file__).resolve().parents[3] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    from runtime_bootstrap import ensure_plugin_runtime_or_exit
except ImportError:  # pragma: no cover - exercised by isolated script tests
    ensure_plugin_runtime_or_exit = None

if ensure_plugin_runtime_or_exit is not None:
    ensure_plugin_runtime_or_exit(__file__)

try:
    import yaml
except ImportError:  # pragma: no cover - exercised through CLI error path
    yaml = None

from plan_parser import parse_plan


MAX_CONFIG_BYTES = 1 * 1024 * 1024
MAX_PLAN_SIDECAR_BYTES = 5 * 1024 * 1024


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


def _plan_json_candidates(plan_path: Path) -> list[Path]:
    suffix = plan_path.suffix.lower()
    if suffix == ".docx":
        return [plan_path.with_suffix(".plan.json")]
    if suffix in (".md", ".markdown", ".txt"):
        return [plan_path.with_suffix(".json")]
    return []


def _read_capped_text(path: Path, *, max_bytes: int, label: str) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Could not stat {label}: {exc}") from exc
    if size > max_bytes:
        raise ValueError(
            f"{label.capitalize()} exceeds the {max_bytes}-byte limit: {path}"
        )
    return path.read_text(encoding="utf-8")


def _sidecar_is_fresh(plan_path: Path, sidecar_path: Path) -> bool:
    try:
        return sidecar_path.stat().st_mtime_ns >= plan_path.stat().st_mtime_ns
    except OSError:
        return False


def _first_present(mapping: dict, *keys: str):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _as_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def _as_text_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    compacted: list[str] = []
    for item in items:
        text = str(item).strip()
        if text:
            compacted.append(text)
    return compacted


def _normalize_day_payload(day_payload: dict) -> dict:
    return {
        "date": _as_text(_first_present(day_payload, "dt", "date")),
        "day_name": _as_text(_first_present(day_payload, "n", "day_name")),
        "standards": _as_text_list(_first_present(day_payload, "st", "standards")),
        "learning_intention": _as_text(
            _first_present(day_payload, "li", "learning_intention")
        ),
        "success_criteria": _as_text_list(
            _first_present(day_payload, "sc", "success_criteria")
        ),
        "agenda": _as_text_list(_first_present(day_payload, "ag", "agenda")),
        "materials": _as_text_list(_first_present(day_payload, "m", "materials")),
        "differentiation": _as_text_list(
            _first_present(day_payload, "df", "differentiation")
        ),
        "evidence": _as_text(_first_present(day_payload, "e", "evidence")),
        "do_now": _as_text(_first_present(day_payload, "do", "do_now")),
    }


def _normalize_plan_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Plan JSON sidecar must decode to a JSON object.")

    raw_days = _first_present(payload, "d", "days")
    if not isinstance(raw_days, list):
        raise ValueError("Plan JSON sidecar must include a day list.")

    days: list[dict] = []
    for day_payload in raw_days:
        if not isinstance(day_payload, dict):
            raise ValueError("Plan JSON sidecar day entries must be JSON objects.")
        normalized = _normalize_day_payload(day_payload)
        if normalized["date"]:
            days.append(normalized)

    if not days:
        raise ValueError("Plan JSON sidecar does not contain any dated lesson days.")

    return {
        "week_of": _as_text(_first_present(payload, "w", "week_of")),
        "subject": _as_text(_first_present(payload, "s", "subject")),
        "teacher": _as_text(_first_present(payload, "t", "teacher")),
        "days": days,
    }


def _plan_payload_from_markdown(plan_md: str) -> dict:
    week = parse_plan(plan_md)
    return {
        "week_of": week.week_of,
        "subject": week.subject,
        "teacher": week.teacher,
        "days": [
            {
                "date": day.date,
                "day_name": day.day_name,
                "standards": list(day.standards),
                "learning_intention": day.learning_intention,
                "success_criteria": list(day.success_criteria),
                "agenda": list(day.agenda),
                "materials": list(day.materials),
                "differentiation": list(day.differentiation),
                "evidence": day.evidence,
                "do_now": day.do_now,
            }
            for day in week.days
        ],
    }


def load_structured_plan(plan_path: Path, *, plan_md: str | None = None) -> dict:
    """Load normalized plan data, preferring a fresh JSON sidecar when present."""
    for candidate in _plan_json_candidates(plan_path):
        if not candidate.exists() or not _sidecar_is_fresh(plan_path, candidate):
            continue
        try:
            payload = json.loads(
                _read_capped_text(
                    candidate,
                    max_bytes=MAX_PLAN_SIDECAR_BYTES,
                    label="plan JSON sidecar",
                )
            )
            return _normalize_plan_payload(payload)
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            continue

    if plan_md is None:
        raise ValueError(
            "No valid plan JSON sidecar found and no markdown fallback was provided."
        )
    return _plan_payload_from_markdown(plan_md)


def load_structured_day(
    plan_path: Path, target_date: str, *, plan_md: str | None = None
) -> dict | None:
    """Return one normalized lesson day plus shared week metadata."""
    plan_payload = load_structured_plan(plan_path, plan_md=plan_md)
    for day in plan_payload["days"]:
        if day["date"] != target_date:
            continue
        merged = {
            "date": day["date"],
            "day_name": day["day_name"],
            "standards": list(day["standards"]),
            "learning_intention": day["learning_intention"],
            "success_criteria": list(day["success_criteria"]),
            "agenda": list(day["agenda"]),
            "materials": list(day["materials"]),
            "differentiation": list(day["differentiation"]),
            "evidence": day["evidence"],
            "do_now": day["do_now"],
            "subject": plan_payload["subject"],
            "teacher": plan_payload["teacher"],
            "week_of": plan_payload["week_of"],
        }
        return merged
    return None


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
