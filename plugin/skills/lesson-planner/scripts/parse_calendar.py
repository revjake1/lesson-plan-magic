#!/usr/bin/env python3
"""parse_calendar.py — .ics/.pdf school calendar → structured non-instructional days.

Usage:
  python parse_calendar.py --input path/to/school-calendar.ics
                           [--range 2026-04-01:2026-06-15]
                           [--subject chem]
                           [--cache-dir ~/Documents/Lesson Plan Magic/.cache/cal]
                           [--pretty]
  python parse_calendar.py --input path/to/school-calendar.pdf
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

_SHARED_DIR = Path(__file__).resolve().parents[3] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

try:
    from runtime_bootstrap import ensure_plugin_runtime_or_exit
except ImportError:  # pragma: no cover - exercised by isolated script tests
    ensure_plugin_runtime_or_exit = None

if ensure_plugin_runtime_or_exit is not None:
    ensure_plugin_runtime_or_exit(__file__)


SUBJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SCHOOL_YEAR_RE = re.compile(r"\b(?P<start>\d{4})\s*[-/]\s*(?P<end>\d{4})\b")

MONTH_NAME_TO_NUMBER = {
    name.lower(): i for i, name in enumerate(calendar.month_name) if i
}
MONTH_NAME_TO_NUMBER.update({
    name[:3].lower(): i for i, name in enumerate(calendar.month_name) if i
})
MONTH_TOKEN_RE = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)
PDF_MONTH_HEADER_RE = re.compile(
    rf"^(?P<month>{MONTH_TOKEN_RE})\.?(?:\s+(?P<year>\d{{4}}))?"
    rf"(?:\s+calendar)?$",
    re.I,
)
PDF_MONTH_DAY_RE = re.compile(
    rf"^(?P<month>{MONTH_TOKEN_RE})\.?\s+"
    rf"(?P<start>\d{{1,2}})(?:\s*[-\u2013]\s*(?P<end>\d{{1,2}}))?"
    rf"(?:,?\s*(?P<year>\d{{2,4}}))?\s+(?P<summary>.+)$",
    re.I,
)
PDF_DAY_RE = re.compile(
    r"^(?:(?:mon|monday|tue|tues|tuesday|wed|wednesday|thu|thur|thurs|thursday|"
    r"fri|friday|sat|saturday|sun|sunday)\.?,?\s+)?"
    r"(?P<start>\d{1,2})(?:\s*[-\u2013]\s*(?P<end>\d{1,2}))?\s+"
    r"(?P<summary>.+)$",
    re.I,
)
PDF_NUMERIC_DATE_RE = re.compile(
    r"^(?P<month>\d{1,2})/(?P<day>\d{1,2})(?:/(?P<year>\d{2,4}))?\s+"
    r"(?P<summary>.+)$"
)


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


def _coerce_year(value: str | None) -> int | None:
    if not value:
        return None
    year = int(value)
    if year < 100:
        return 2000 + year
    return year


def _month_number(token: str) -> int | None:
    return MONTH_NAME_TO_NUMBER.get(token.strip().strip(".").lower())


def _normalize_pdf_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip().strip("-\u2022\u25aa\u25cf ")


def _parse_school_year(text: str) -> tuple[int, int] | None:
    if not (m := SCHOOL_YEAR_RE.search(text)):
        return None
    start, end = int(m.group("start")), int(m.group("end"))
    if end < start:
        start, end = end, start
    return start, end


def _resolve_month_year(
    month: int,
    *,
    year: int | None,
    current_year: int | None,
    current_month: int | None,
    school_year: tuple[int, int] | None,
) -> int | None:
    if year is not None:
        return year
    if current_year is not None:
        if current_month is not None and month < current_month:
            return current_year + 1
        return current_year
    if school_year:
        start_year, end_year = school_year
        # Typical K-12 calendars split the year around summer.
        return start_year if month >= 7 else end_year
    return None


def _expand_date_span(start: date, end: date) -> list[date]:
    if end < start:
        return []
    out: list[date] = []
    cursor = start
    while cursor <= end:
        out.append(cursor)
        cursor += timedelta(days=1)
    return out


def _build_pdf_dates(
    *,
    year: int | None,
    month: int,
    start_day: int,
    end_day: int | None = None,
) -> list[date]:
    if year is None:
        return []
    try:
        start = date(year, month, start_day)
        end = date(year, month, end_day or start_day)
    except ValueError:
        return []
    return _expand_date_span(start, end)


def _parse_pdf_month_header(
    line: str,
    *,
    current_year: int | None,
    current_month: int | None,
    school_year: tuple[int, int] | None,
) -> tuple[int, int] | None:
    if not (m := PDF_MONTH_HEADER_RE.fullmatch(line)):
        return None
    month = _month_number(m.group("month"))
    if month is None:
        return None
    year = _resolve_month_year(
        month,
        year=_coerce_year(m.group("year")),
        current_year=current_year,
        current_month=current_month,
        school_year=school_year,
    )
    if year is None:
        return None
    return year, month


def _parse_pdf_event_line(
    line: str,
    *,
    current_year: int | None,
    current_month: int | None,
    school_year: tuple[int, int] | None,
) -> tuple[list[date], str] | None:
    if m := PDF_NUMERIC_DATE_RE.match(line):
        year = _coerce_year(m.group("year")) or current_year
        if not year:
            return None
        try:
            d = date(year, int(m.group("month")), int(m.group("day")))
        except ValueError:
            return None
        return [d], m.group("summary").strip()

    if m := PDF_MONTH_DAY_RE.match(line):
        month = _month_number(m.group("month"))
        if month is None:
            return None
        year = _resolve_month_year(
            month,
            year=_coerce_year(m.group("year")),
            current_year=current_year,
            current_month=current_month,
            school_year=school_year,
        )
        dates = _build_pdf_dates(
            year=year,
            month=month,
            start_day=int(m.group("start")),
            end_day=int(m.group("end")) if m.group("end") else None,
        )
        if not dates:
            return None
        return dates, m.group("summary").strip()

    if current_year is None or current_month is None:
        return None
    if not (m := PDF_DAY_RE.match(line)):
        return None
    dates = _build_pdf_dates(
        year=current_year,
        month=current_month,
        start_day=int(m.group("start")),
        end_day=int(m.group("end")) if m.group("end") else None,
    )
    if not dates:
        return None
    return dates, m.group("summary").strip()


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


def parse_pdf_text(text: str, *, warn: bool = False) -> list[tuple[date, str]]:
    """Parse extractable-text PDF calendar content into (date, summary) pairs.

    The supported PDF layout is intentionally conservative:
      - a school-year title may contain a year span like ``2026-2027``
      - month headers appear as ``August 2026`` or ``September``
      - event lines appear as ``7 Labor Day - No School`` or
        ``11-15 Thanksgiving Break`` within the current month section
      - fully qualified lines like ``8/10/2026 Teacher Work Day`` and
        ``August 10 Teacher Work Day`` are also accepted
    """
    school_year = _parse_school_year(text)
    current_year = None
    current_month = None
    events: list[tuple[date, str]] = []

    for raw_line in text.splitlines():
        line = _normalize_pdf_line(raw_line)
        if not line:
            continue

        if context := _parse_pdf_month_header(
            line,
            current_year=current_year,
            current_month=current_month,
            school_year=school_year,
        ):
            current_year, current_month = context
            continue

        if parsed := _parse_pdf_event_line(
            line,
            current_year=current_year,
            current_month=current_month,
            school_year=school_year,
        ):
            dates, summary = parsed
            events.extend((d, summary) for d in dates)

    if warn and not events:
        print("warning: found no extractable calendar events in PDF", file=sys.stderr)

    return events


def parse_pdf(path: Path, *, warn: bool = False) -> list[tuple[date, str]]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return parse_pdf_text("\n\n".join(pages), warn=warn)


def _path_looks_like_pdf(path: Path) -> bool:
    if path.suffix.lower() == ".pdf":
        return True
    try:
        with path.open("rb") as fh:
            return fh.read(5) == b"%PDF-"
    except OSError:
        return False


def parse_calendar_file(
    path: Path,
    range_end: date | None = None,
    *,
    warn: bool = False,
) -> list[tuple[date, str]]:
    if _path_looks_like_pdf(path):
        return parse_pdf(path, warn=warn)
    text = path.read_text(encoding="utf-8", errors="replace")
    return parse_ics(text, range_end=range_end, warn=warn)


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
    ap.add_argument("--input", required=True, help="Path to .ics or .pdf file")
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

    events = parse_calendar_file(input_path, range_end=end, warn=True)
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
