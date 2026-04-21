#!/usr/bin/env python3
"""parse_calendar.py — .ics school calendar → structured non-instructional days.

Usage:
  python parse_calendar.py --input path/to/school-calendar.ics
                           [--range 2026-04-01:2026-06-15]
                           [--subject chem]
                           [--cache-dir ~/Documents/Lesson Plan Magic/.cache/cal]
                           [--pretty]

Output: dense JSON by default (short keys, nulls dropped) — the plan
pipeline reads this, not humans. Pass --pretty for readable stdout.

Dense schema:
  {r:[start,end], n: int non-instructional-day-count,
   D:[{d:YYYY-MM-DD, t:category, s:summary?}, ...]}

Category codes:
  H  — holiday / break
  P  — professional development / teacher work day
  T  — testing window (ACT, state tests, EOC, etc.)
  E  — early release / half day
  A  — assembly / field trip / special schedule
  O  — other (unclassified)
"""
from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


SUBJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


CATEGORY_KEYWORDS = [
    ("H", re.compile(r"\b(holiday|break|no school|closed|labor day|thanksgiving|winter|spring break|fall break|memorial|juneteenth|christmas|new year|mlk|presidents|veterans|columbus|indigenous)\b", re.I)),
    ("P", re.compile(r"\b(pd|professional development|inservice|in-service|teacher work|planning day|post-planning|pre-planning|workshop)\b", re.I)),
    ("T", re.compile(r"\b(testing|test|exam|eoc|mcas|staar|ap\s+\w+\s+exam|ap exam|psat|sat|iready|istation|nwea|state assessment|benchmark|milestones)\b", re.I)),
    ("E", re.compile(r"\b(early release|early dismissal|half day|half-day|shortened)\b", re.I)),
    ("A", re.compile(r"\b(assembly|field trip|pep rally|homecoming|awards ceremony|spirit)\b", re.I)),
]


def _classify(summary: str) -> str:
    if not summary:
        return "O"
    for code, pat in CATEGORY_KEYWORDS:
        if pat.search(summary):
            return code
    return "O"


def _parse_dtstart(value: str) -> date | None:
    """Accept DTSTART forms: 20260401, 20260401T080000Z, 20260401T080000."""
    v = value.strip()
    try:
        if "T" in v:
            v = v.split("T", 1)[0]
        if len(v) == 8 and v.isdigit():
            return date(int(v[:4]), int(v[4:6]), int(v[6:]))
        if "-" in v:
            return date.fromisoformat(v)
    except ValueError:
        return None
    return None


# RFC 5545 BYDAY token → Python weekday index (Monday=0, Sunday=6).
_BYDAY_INDEX = {
    "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6,
}


def _parse_byday(byday: str) -> list[int]:
    """Parse a BYDAY value (``"MO,WE,FR"``) into weekday indices.

    Ignores numeric prefixes used for monthly-nth-weekday rules
    (``"1MO"``, ``"-1FR"``) because K-12 calendars use monthly BYDAY
    only rarely and we don't currently expand MONTHLY with BYDAY. For
    WEEKLY, which is what the audit reproducer exercises, the numeric
    prefix is not allowed by RFC 5545 anyway.
    """
    out: list[int] = []
    for raw in byday.split(","):
        token = raw.strip().upper()
        if not token:
            continue
        # Strip a leading signed integer prefix ("-1FR", "2MO") if present.
        i = 0
        if i < len(token) and token[i] in "+-":
            i += 1
        while i < len(token) and token[i].isdigit():
            i += 1
        day_code = token[i:]
        if day_code in _BYDAY_INDEX:
            out.append(_BYDAY_INDEX[day_code])
    return out


def _expand_rrule(
    dtstart: date,
    rrule: str,
    range_end: date | None,
    *,
    include_dtstart: bool = False,
) -> list[date]:
    """Expand a simple RRULE into a list of occurrence dates.

    Supports the subset K-12 calendars actually use:
      FREQ=WEEKLY/MONTHLY/YEARLY with optional COUNT, UNTIL, INTERVAL, BYDAY.
    BYDAY is honored for WEEKLY (e.g. ``FREQ=WEEKLY;BYDAY=MO,WE``
    expands to both Mondays and Wednesdays within the window).
    Falls back to [] for anything we can't parse.

    ``include_dtstart`` controls whether DTSTART itself is returned
    when it's a valid member of the recurrence set. The ``parse_ics``
    caller emits DTSTART separately for events with no RRULE, but when
    RRULE is present it asks the expander to be authoritative about
    the full set — which is RFC-correct when BYDAY excludes DTSTART's
    weekday (e.g. DTSTART=Monday but BYDAY=TU,TH).
    """
    if not rrule:
        return []

    parts = {}
    for token in rrule.split(";"):
        if "=" in token:
            k, v = token.split("=", 1)
            parts[k.upper()] = v

    freq = parts.get("FREQ", "").upper()
    interval = max(int(parts.get("INTERVAL", "1")), 1)
    count = int(parts["COUNT"]) if "COUNT" in parts else None
    until = _parse_dtstart(parts["UNTIL"]) if "UNTIL" in parts else None
    byday = _parse_byday(parts["BYDAY"]) if "BYDAY" in parts else []

    # Cap expansion to avoid runaway loops — 2 school years max
    cap_date = range_end or (dtstart + timedelta(days=730))
    if until:
        cap_date = min(cap_date, until)

    # Hard cap to avoid runaway loops when neither COUNT, UNTIL, nor a
    # range is given and BYDAY generates >1 occurrence per week.
    max_occurrences = count or 400

    # --- WEEKLY with BYDAY: expand each named weekday per INTERVAL ---
    if freq == "WEEKLY" and byday:
        occurrences: list[date] = []
        # Week anchor = the Monday of DTSTART's week. This keeps us
        # aligned to RFC 5545's default WKST=MO. We don't implement
        # WKST overrides — K-12 calendars don't use it.
        anchor = dtstart - timedelta(days=dtstart.weekday())
        week_index = 0
        while len(occurrences) < max_occurrences:
            week_start = anchor + timedelta(weeks=week_index * interval)
            if week_start > cap_date:
                break
            week_any_in_window = False
            for wd in sorted(byday):
                d = week_start + timedelta(days=wd)
                if d < dtstart:
                    continue
                if d > cap_date:
                    continue
                week_any_in_window = True
                occurrences.append(d)
                if len(occurrences) >= max_occurrences:
                    break
            # Stop if we've walked past cap_date for an entire week.
            if not week_any_in_window and week_start > cap_date - timedelta(days=7):
                break
            week_index += 1

        # Respect the caller's DTSTART emission policy. When the caller
        # already emitted DTSTART separately (include_dtstart=False), we
        # drop it from the expansion if it coincides with a BYDAY match.
        # When the caller wants the authoritative set, keep it.
        if not include_dtstart and occurrences and occurrences[0] == dtstart:
            occurrences = occurrences[1:]
        return occurrences

    if freq == "WEEKLY":
        delta = timedelta(weeks=interval)
    elif freq == "MONTHLY":
        delta = None  # handled below
    elif freq == "YEARLY":
        delta = None
    elif freq == "DAILY":
        delta = timedelta(days=interval)
    else:
        return []

    occurrences: list[date] = []
    current = dtstart
    anchor_day = dtstart.day
    for _ in range(max_occurrences):
        if current > cap_date:
            break
        occurrences.append(current)

        if freq == "MONTHLY":
            month = current.month - 1 + interval
            year = current.year + month // 12
            month = month % 12 + 1
            day = min(anchor_day, calendar.monthrange(year, month)[1])
            current = date(year, month, day)
        elif freq == "YEARLY":
            try:
                current = date(current.year + interval, current.month, current.day)
            except ValueError:
                break
        else:
            current = current + delta

    # Honor include_dtstart. Default preserves the pre-0.2.2 contract
    # where dtstart is emitted separately by the caller.
    if include_dtstart:
        return occurrences
    return occurrences[1:] if occurrences else []


def parse_ics(
    text: str,
    range_end: date | None = None,
    *,
    warn: bool = False,
) -> list[tuple[date, str]]:
    """Parse ICS text into (date, summary) pairs.

    Handles:
      - Fold-wrapped lines (RFC 5545)
      - DTEND for multi-day events (expands to one entry per day)
      - RRULE for recurring events (weekly assemblies, etc.)
    """
    # Unfold: continuation lines begin with a single space or tab.
    unfolded: list[str] = []
    for line in text.splitlines():
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)

    events: list[tuple[date, str]] = []
    skipped_events = 0
    in_event = False
    current: dict[str, str] = {}
    for line in unfolded:
        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
        elif line == "END:VEVENT":
            if current.get("DTSTART") and (d := _parse_dtstart(current["DTSTART"])):
                summary = current.get("SUMMARY", "").strip()

                # Determine span from DTEND
                dtend = _parse_dtstart(current["DTEND"]) if current.get("DTEND") else None

                rrule = current.get("RRULE")
                if rrule:
                    # Ask the expander for the authoritative set — this
                    # correctly excludes DTSTART when BYDAY doesn't cover
                    # its weekday (RFC 5545 behavior matching dateutil).
                    # Multi-day DTSTART+DTEND spans are extremely rare
                    # with RRULE in K-12 calendars, so we treat each
                    # recurrence as a single-day event here.
                    for rd in _expand_rrule(
                        d, rrule, range_end, include_dtstart=True
                    ):
                        events.append((rd, summary))
                elif dtend and dtend > d:
                    # Multi-day event: emit one entry per day.
                    # For all-day ICS events DTEND is exclusive (the day *after*
                    # the last day), so we iterate up to but not including dtend.
                    cursor = d
                    while cursor < dtend:
                        events.append((cursor, summary))
                        cursor += timedelta(days=1)
                else:
                    events.append((d, summary))
            elif current:
                skipped_events += 1

            in_event = False
            current = {}
        elif in_event and ":" in line:
            key, value = line.split(":", 1)
            key = key.split(";", 1)[0]
            if key in ("DTSTART", "DTEND", "SUMMARY", "DESCRIPTION", "RRULE"):
                current[key] = value
    if warn and skipped_events:
        print(
            f"warning: skipped {skipped_events} malformed VEVENT(s)",
            file=sys.stderr,
        )
    return events


def in_range(d: date, start: date | None, end: date | None) -> bool:
    if start and d < start:
        return False
    if end and d > end:
        return False
    return True


def _parse_range(s: str) -> tuple[date, date]:
    a, b = s.split(":", 1)
    return date.fromisoformat(a), date.fromisoformat(b)


def validate_subject_id(subject_id: str) -> str:
    if not SUBJECT_ID_RE.fullmatch(subject_id or ""):
        raise ValueError(
            "subject id must be kebab-case (lowercase letters, digits, hyphens only)"
        )
    return subject_id


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to .ics file")
    ap.add_argument(
        "--range",
        help="ISO date range filter, e.g. 2026-04-01:2026-06-15",
    )
    ap.add_argument("--subject", help="Subject id (cache filename)")
    ap.add_argument("--cache-dir", help="Cache directory")
    ap.add_argument(
        "--pretty", action="store_true",
        help="Pretty-print stdout (default: dense JSON)",
    )
    args = ap.parse_args()
    try:
        subject_id = validate_subject_id(args.subject) if args.subject else None
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    input_path = Path(args.input).expanduser()
    if not input_path.exists():
        print(f"error: file not found: {input_path}", file=sys.stderr)
        return 1

    start = end = None
    if args.range:
        try:
            start, end = _parse_range(args.range)
        except ValueError:
            print(
                "error: --range must be YYYY-MM-DD:YYYY-MM-DD",
                file=sys.stderr,
            )
            return 1

    text = input_path.read_text(encoding="utf-8", errors="replace")
    events = parse_ics(text, range_end=end, warn=True)
    events = [(d, s) for d, s in events if in_range(d, start, end)]

    days = []
    for d, summary in sorted(events, key=lambda x: x[0]):
        entry = {
            "d": d.isoformat(),
            "t": _classify(summary),
        }
        if summary:
            entry["s"] = summary
        days.append(entry)

    payload = {
        "r": [
            start.isoformat() if start else None,
            end.isoformat() if end else None,
        ],
        "n": len(days),
        "D": days,
    }
    # Drop null-valued top-level fields
    if payload["r"] == [None, None]:
        payload.pop("r")

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, separators=(",", ":")))

    if args.cache_dir and subject_id:
        cdir = Path(args.cache_dir).expanduser()
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / f"{subject_id}.calendar.json").write_text(
            json.dumps(payload, separators=(",", ":"))
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
