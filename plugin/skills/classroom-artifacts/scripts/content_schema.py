#!/usr/bin/env python3
"""Schema validation for classroom-artifacts content JSON payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


class ContentValidationError(ValueError):
    """Raised when artifact content JSON is malformed or schema-invalid."""


MAX_CONTENT_BYTES = 1 * 1024 * 1024


def load_and_validate_content(
    *,
    content_file: str | None,
    content_json: str | None,
    validator: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    if content_file:
        raw = _read_content_file(Path(content_file))
        source = str(Path(content_file))
    elif content_json:
        raw = content_json
        source = "--content-json"
    else:
        return {}

    _enforce_size_limit(raw, source=source)
    data = _load_json_object(raw, source=source)
    return validator(data)


def validate_exit_ticket_content(data: dict[str, Any]) -> dict[str, Any]:
    _reject_unknown_keys(
        data,
        {"learning_intention", "questions", "metacognitive"},
    )
    out: dict[str, Any] = {}
    if "learning_intention" in data:
        out["learning_intention"] = _expect_string(
            data["learning_intention"], "content.learning_intention"
        )
    if "questions" in data:
        out["questions"] = _expect_string_list(
            data["questions"], "content.questions", allow_single=True
        )
    if "metacognitive" in data:
        out["metacognitive"] = _expect_string(
            data["metacognitive"], "content.metacognitive"
        )
    return out


def validate_do_now_content(data: dict[str, Any]) -> dict[str, Any]:
    _reject_unknown_keys(
        data,
        {"prompt", "context", "instructions", "period"},
    )
    out: dict[str, Any] = {}
    for key in ("prompt", "context", "instructions", "period"):
        if key in data:
            out[key] = _expect_string(data[key], f"content.{key}")
    return out


def validate_agenda_content(data: dict[str, Any]) -> dict[str, Any]:
    _reject_unknown_keys(
        data,
        {"agenda", "homework", "materials"},
    )
    out: dict[str, Any] = {}
    if "agenda" in data:
        out["agenda"] = _expect_string_list(
            data["agenda"], "content.agenda", allow_single=True
        )
    if "homework" in data:
        homework = data["homework"]
        if isinstance(homework, list):
            out["homework"] = "\n".join(
                _expect_string_list(homework, "content.homework")
            )
        else:
            out["homework"] = _expect_string(homework, "content.homework")
    if "materials" in data:
        out["materials"] = _expect_string_list(
            data["materials"], "content.materials", allow_single=True
        )
    return out


def validate_sub_plan_content(data: dict[str, Any]) -> dict[str, Any]:
    _reject_unknown_keys(
        data,
        {
            "learning_focus",
            "periods",
            "activity",
            "materials",
            "backup",
            "emergency",
            "return_notes",
        },
    )
    out: dict[str, Any] = {}
    if "learning_focus" in data:
        out["learning_focus"] = _expect_string(
            data["learning_focus"], "content.learning_focus"
        )
    if "periods" in data:
        out["periods"] = _expect_string(data["periods"], "content.periods")
    if "activity" in data:
        out["activity"] = _expect_activity(data["activity"], "content.activity")
    if "materials" in data:
        out["materials"] = _expect_string_list(
            data["materials"], "content.materials", allow_single=True
        )
    if "backup" in data:
        out["backup"] = _expect_string(data["backup"], "content.backup")
    if "emergency" in data:
        out["emergency"] = _expect_emergency(
            data["emergency"], "content.emergency"
        )
    if "return_notes" in data:
        out["return_notes"] = _expect_string(
            data["return_notes"], "content.return_notes"
        )
    return out


def _read_content_file(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ContentValidationError(f"Could not stat content file: {exc}") from exc
    if size > MAX_CONTENT_BYTES:
        raise ContentValidationError(
            f"{path} exceeds the {MAX_CONTENT_BYTES}-byte content limit."
        )
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContentValidationError(f"Could not read content file: {exc}") from exc


def _enforce_size_limit(raw: str, *, source: str) -> None:
    if len(raw.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise ContentValidationError(
            f"{source} exceeds the {MAX_CONTENT_BYTES}-byte content limit."
        )


def _load_json_object(raw: str, *, source: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ContentValidationError(f"{source} is not valid JSON: {exc}") from exc
    if data is None:
        raise ContentValidationError(
            f"{source} must decode to a JSON object, not JSON null."
        )
    if not isinstance(data, dict):
        raise ContentValidationError(f"{source} must decode to a JSON object.")
    return data


def _reject_unknown_keys(data: dict[str, Any], allowed: set[str]) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ContentValidationError(
            "Unknown content key(s): " + ", ".join(unknown)
        )


def _expect_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ContentValidationError(f"{path} must be a string.")
    return value


def _expect_string_list(
    value: Any, path: str, *, allow_single: bool = False
) -> list[str]:
    if allow_single and isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        raise ContentValidationError(f"{path} must be a list of strings.")
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ContentValidationError(f"{path}[{i}] must be a string.")
        out.append(item)
    return out


def _expect_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContentValidationError(f"{path} must be an integer.")
    return value


def _expect_activity(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContentValidationError(f"{path} must be an object.")
    _reject_unknown_keys(value, {"steps", "estimated_min"})
    out: dict[str, Any] = {}
    if "steps" in value:
        out["steps"] = _expect_string_list(
            value["steps"], f"{path}.steps", allow_single=True
        )
    if "estimated_min" in value:
        out["estimated_min"] = _expect_int(
            value["estimated_min"], f"{path}.estimated_min"
        )
    return out


def _expect_emergency(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContentValidationError(f"{path} must be an object.")
    _reject_unknown_keys(value, {"nearby_teacher", "office_extension"})
    out: dict[str, Any] = {}
    for key in ("nearby_teacher", "office_extension"):
        if key in value:
            out[key] = _expect_string(value[key], f"{path}.{key}")
    return out
