"""Pytest regression tests for parse_calendar.py BYDAY fix."""

import subprocess
import sys
from pathlib import Path

import pytest
from datetime import date

from parse_calendar import _expand_rrule, parse_ics


SCRIPT_PATH = (
    Path(__file__).parent.parent
    / "skills" / "lesson-planner" / "scripts" / "parse_calendar.py"
)


class TestExpandRruleWeeklyWithByday:
    """Test _expand_rrule with FREQ=WEEKLY and BYDAY."""

    def test_weekly_byday_mon_wed_count_4(self):
        """FREQ=WEEKLY;BYDAY=MO,WE;COUNT=4 with Monday start.

        Should return exactly [Mon, Wed, Mon, Wed] = 4 occurrences.
        2026-04-06 is a Monday, so: 04-06, 04-08, 04-13, 04-15.
        """
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;BYDAY=MO,WE;COUNT=4"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=True)

        expected = [
            date(2026, 4, 6),   # Monday
            date(2026, 4, 8),   # Wednesday
            date(2026, 4, 13),  # Monday
            date(2026, 4, 15),  # Wednesday
        ]
        assert result == expected

    def test_weekly_byday_tue_thu_monday_start(self):
        """FREQ=WEEKLY;BYDAY=TU,TH;COUNT=4 with Monday start.

        Should start with 04-07 (Tuesday), not 04-06 (Monday),
        since BYDAY excludes Monday. Should give 4 occurrences:
        Tue, Thu, Tue, Thu = [04-07, 04-09, 04-14, 04-16].
        """
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;BYDAY=TU,TH;COUNT=4"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=True)

        expected = [
            date(2026, 4, 7),   # Tuesday
            date(2026, 4, 9),   # Thursday
            date(2026, 4, 14),  # Tuesday
            date(2026, 4, 16),  # Thursday
        ]
        assert result == expected

    def test_weekly_no_byday_uses_legacy_behavior(self):
        """FREQ=WEEKLY without BYDAY repeats DTSTART weekly (legacy)."""
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;COUNT=3"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=False)

        # With include_dtstart=False (legacy default), skip DTSTART in output
        # Should get [Mon+7days, Mon+14days] = [04-13, 04-20]
        expected = [
            date(2026, 4, 13),  # Monday + 1 week
            date(2026, 4, 20),  # Monday + 2 weeks
        ]
        assert result == expected

    def test_weekly_no_byday_with_include_dtstart_true(self):
        """FREQ=WEEKLY without BYDAY with include_dtstart=True includes DTSTART."""
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;COUNT=3"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=True)

        # With include_dtstart=True, include DTSTART as first element
        expected = [
            date(2026, 4, 6),   # DTSTART
            date(2026, 4, 13),  # Monday + 1 week
            date(2026, 4, 20),  # Monday + 2 weeks
        ]
        assert result == expected

    def test_weekly_byday_exclude_dtstart_when_not_in_byday(self):
        """When BYDAY excludes DTSTART's weekday, DTSTART is excluded.

        BYDAY=TU,TH with Monday DTSTART should start with Tuesday,
        not Monday. With include_dtstart=False, we drop DTSTART anyway
        (pre-0.2.2 behavior).
        """
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;BYDAY=TU,TH;COUNT=4"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=False)

        # First occurrence is Tuesday (04-07), not Monday
        assert result[0] == date(2026, 4, 7)
        assert len(result) == 4

    def test_weekly_byday_with_interval(self):
        """FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE every other week."""
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE;COUNT=4"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=True)

        # Week 0: 04-06 (Mon), 04-08 (Wed)
        # Week 2: 04-20 (Mon), 04-22 (Wed)
        expected = [
            date(2026, 4, 6),   # Week 0 Monday
            date(2026, 4, 8),   # Week 0 Wednesday
            date(2026, 4, 20),  # Week 2 Monday
            date(2026, 4, 22),  # Week 2 Wednesday
        ]
        assert result == expected


class TestParseIcsWithRrule:
    """Test parse_ics with RRULE events."""

    def test_parse_ics_weekly_byday_mon_wed(self):
        """ICS event with FREQ=WEEKLY;BYDAY=MO,WE;COUNT=4."""
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20260406
DTEND:20260407
SUMMARY:Monday/Wednesday Assembly
RRULE:FREQ=WEEKLY;BYDAY=MO,WE;COUNT=4
UID:test@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics)

        # Should expand to 4 occurrences: Mon, Wed, Mon, Wed
        # Dates should be 04-06, 04-08, 04-13, 04-15
        dates = sorted(set(d for d, _ in result))
        expected_dates = [
            date(2026, 4, 6),
            date(2026, 4, 8),
            date(2026, 4, 13),
            date(2026, 4, 15),
        ]
        assert dates == expected_dates

    def test_parse_ics_weekly_byday_tue_thu(self):
        """ICS event DTSTART=Monday but BYDAY=TU,TH excludes Monday."""
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20260406
DTEND:20260407
SUMMARY:Tuesday/Thursday Class
RRULE:FREQ=WEEKLY;BYDAY=TU,TH;COUNT=4
UID:test@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics)

        dates = sorted(set(d for d, _ in result))
        expected_dates = [
            date(2026, 4, 7),   # Tuesday
            date(2026, 4, 9),   # Thursday
            date(2026, 4, 14),  # Tuesday
            date(2026, 4, 16),  # Thursday
        ]
        assert dates == expected_dates
        # Verify DTSTART (04-06, Monday) is NOT in the list
        assert date(2026, 4, 6) not in dates

    def test_parse_ics_no_rrule_multiday(self):
        """ICS event with DTEND > DTSTART but no RRULE expands per day."""
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20260406
DTEND:20260409
SUMMARY:Three-Day Event
UID:test@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics)

        dates = sorted(set(d for d, _ in result))
        # DTEND is exclusive, so should emit 04-06, 04-07, 04-08 (not 04-09)
        expected_dates = [
            date(2026, 4, 6),
            date(2026, 4, 7),
            date(2026, 4, 8),
        ]
        assert dates == expected_dates

    def test_parse_ics_single_day(self):
        """ICS event with DTEND = DTSTART + 1 day (single all-day event)."""
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20260406
DTEND:20260407
SUMMARY:Assembly Day
UID:test@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics)

        dates = [d for d, _ in result]
        assert dates == [date(2026, 4, 6)]

    def test_parse_ics_preserves_summary(self):
        """ICS parsing preserves event summary."""
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20260406
DTEND:20260407
SUMMARY:Teacher Work Day
UID:test@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics)

        _, summary = result[0]
        assert summary == "Teacher Work Day"

    def test_parse_ics_multiple_events(self):
        """ICS with multiple VEVENT blocks."""
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20260406
DTEND:20260407
SUMMARY:Event 1
UID:test1@example.com
END:VEVENT
BEGIN:VEVENT
DTSTART:20260410
DTEND:20260411
SUMMARY:Event 2
UID:test2@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics)

        assert len(result) == 2
        dates = [d for d, _ in result]
        assert date(2026, 4, 6) in dates
        assert date(2026, 4, 10) in dates


class TestExpandRruleEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty_rrule_returns_empty(self):
        """Empty RRULE string returns empty list."""
        result = _expand_rrule(date(2026, 4, 6), "", None)
        assert result == []

    def test_byday_sorts_occurrences(self):
        """Occurrences within a week are returned in order."""
        dtstart = date(2026, 4, 6)  # Monday
        rrule = "FREQ=WEEKLY;BYDAY=FR,MO,WE;COUNT=3"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=True)

        # Should return in order: Mon, Wed, Fri (for week 1)
        assert result[0].weekday() == 0  # Monday
        assert result[1].weekday() == 2  # Wednesday
        assert result[2].weekday() == 4  # Friday

    def test_count_zero_or_negative(self):
        """COUNT=0 or missing defaults to no explicit limit."""
        dtstart = date(2026, 4, 6)
        rrule = "FREQ=WEEKLY;BYDAY=MO"

        # Without COUNT, the expansion should have a default cap
        result = _expand_rrule(dtstart, rrule, range_end=date(2026, 4, 20), include_dtstart=True)
        assert len(result) > 0
        assert all(d <= date(2026, 4, 20) for d in result)

    def test_monthly_31st_uses_actual_month_end(self):
        dtstart = date(2026, 1, 31)
        rrule = "FREQ=MONTHLY;COUNT=4"

        result = _expand_rrule(dtstart, rrule, range_end=None, include_dtstart=True)

        assert result == [
            date(2026, 1, 31),
            date(2026, 2, 28),
            date(2026, 3, 31),
            date(2026, 4, 30),
        ]

    def test_parse_ics_warns_on_malformed_event(self, capsys):
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:not-a-date
SUMMARY:Broken Event
UID:test@example.com
END:VEVENT
END:VCALENDAR
"""
        result = parse_ics(ics, warn=True)

        assert result == []
        captured = capsys.readouterr()
        assert "skipped 1 malformed VEVENT" in captured.err


class TestParseCalendarCli:
    def test_cli_rejects_non_kebab_subject_id_for_cache_write(self, tmp_path):
        ics_path = tmp_path / "calendar.ics"
        ics_path.write_text(
            "BEGIN:VCALENDAR\n"
            "BEGIN:VEVENT\n"
            "DTSTART;VALUE=DATE:20260422\n"
            "SUMMARY:Holiday\n"
            "END:VEVENT\n"
            "END:VCALENDAR\n",
            encoding="utf-8",
        )
        cache_dir = tmp_path / "cache"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--input",
                str(ics_path),
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
        assert not (tmp_path / "escaped.calendar.json").exists()
        assert not cache_dir.exists()
