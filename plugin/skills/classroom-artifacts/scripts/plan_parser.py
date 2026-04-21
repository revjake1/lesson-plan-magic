#!/usr/bin/env python3
"""Markdown lesson-plan parser shared by classroom-artifacts scripts."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DayPlan:
    date: str
    day_name: str
    standards: list
    learning_intention: str
    success_criteria: list
    agenda: list
    materials: list
    differentiation: list
    evidence: str
    do_now: str = ""


@dataclass
class WeekPlan:
    week_of: str
    subject: str
    teacher: str
    days: list


HEADER_MAP = {
    "standards": "standards",
    "gse standards": "standards",
    "learning intention": "learning_intention",
    "learning intentions": "learning_intention",
    "learning target": "learning_intention",
    "success criteria": "success_criteria",
    "i can": "success_criteria",
    "agenda": "agenda",
    "instructional framework": "agenda",
    "lesson": "agenda",
    "materials": "materials",
    "materials needed": "materials",
    "differentiation": "differentiation",
    "differentiated instruction": "differentiation",
    "evidence of learning": "evidence",
    "evaluation of mastery": "evidence",
    "assessment": "evidence",
    "do now": "do_now",
    "do-now": "do_now",
    "bell ringer": "do_now",
    "bellringer": "do_now",
    "warm-up": "do_now",
    "warm up": "do_now",
    "date": "date",
}

VALID_DAY_HEADER_RE = re.compile(
    r"^## (?P<date>\d{4}-\d{2}-\d{2})(?:\s*[—-]\s*(?P<day_name>.+))?$"
)
LOOSE_DAY_HEADER_RE = re.compile(r"^## (?P<date>\d{4}-\d{1,2}-\d{1,2})\b")


def parse_plan(md: str) -> WeekPlan:
    """Parse markdown lesson plan into a normalized WeekPlan."""
    lines = md.split("\n")
    week_of = subject = teacher = None
    days: list[DayPlan] = []
    current_day: dict | None = None
    current_section: str | None = None
    section_content: list[str] = []

    def flush(day_dict, section, content):
        if day_dict is None:
            return
        if section:
            day_dict[section] = content
        days.append(_day_from_dict(day_dict))

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith("# Week of"):
            week_of = line_stripped.replace("# Week of", "").strip()
        elif line_stripped.startswith("Subject:"):
            subject = line_stripped.replace("Subject:", "").strip()
        elif line_stripped.startswith("Teacher:"):
            teacher = line_stripped.replace("Teacher:", "").strip()
        elif line_stripped.startswith("## "):
            day_header = VALID_DAY_HEADER_RE.match(line_stripped)
            if day_header:
                flush(current_day, current_section, section_content)
                current_day = {
                    "date": day_header.group("date"),
                    "day_name": (day_header.group("day_name") or "Unknown").strip(),
                }
                current_section = None
                section_content = []
                continue
            loose_header = LOOSE_DAY_HEADER_RE.match(line_stripped)
            if loose_header:
                bad_date = loose_header.group("date")
                raise ValueError(
                    f"Invalid day header '{bad_date}'. "
                    "Use zero-padded YYYY-MM-DD in every '##' day heading."
                )
            continue
        elif line_stripped.startswith("###") and current_day is not None:
            if current_section:
                current_day[current_section] = section_content
            current_section = _normalize_header(
                line_stripped.replace("###", "").strip()
            )
            section_content = []
        elif current_day is not None and current_section is not None:
            if not line_stripped:
                continue
            if line_stripped.startswith("-") or line_stripped.startswith("*"):
                section_content.append(line_stripped[1:].strip())
            elif re.match(r"^\d+\.\s+", line_stripped):
                section_content.append(re.sub(r"^\d+\.\s+", "", line_stripped))
            else:
                section_content.append(line_stripped)

    flush(current_day, current_section, section_content)
    if not days:
        raise ValueError(
            "No lesson days found. Expected day headers like "
            "'## 2026-04-22 — Wednesday'."
        )
    return WeekPlan(week_of or "", subject or "", teacher or "", days)


def _normalize_header(header: str) -> str:
    lowered = header.lower().strip(":.")
    for key, value in HEADER_MAP.items():
        if key in lowered:
            return value
    return lowered.replace(" ", "_")


def _day_from_dict(day_dict: dict) -> DayPlan:
    def _as_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _as_str(value):
        if value is None:
            return ""
        if isinstance(value, list):
            return "\n".join(value)
        return str(value)

    return DayPlan(
        date=day_dict.get("date", ""),
        day_name=day_dict.get("day_name", ""),
        standards=_as_list(day_dict.get("standards")),
        learning_intention=_as_str(day_dict.get("learning_intention")),
        success_criteria=_as_list(day_dict.get("success_criteria")),
        agenda=_as_list(day_dict.get("agenda")),
        materials=_as_list(day_dict.get("materials")),
        differentiation=_as_list(day_dict.get("differentiation")),
        evidence=_as_str(day_dict.get("evidence")),
        do_now=_as_str(day_dict.get("do_now")),
    )
