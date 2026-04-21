# Schedule Patterns

How the skill reasons about different bell schedules, school calendars, and
pacing structures.

### Common schedule types to support
- Traditional 7-period (45–55 min)
- Block (4x90 or A/B day)
- Hybrid (e.g., 3 long periods + 2 short)
- Elementary self-contained (one teacher, all subjects)
- Rotating day schedule (day 1 through day 6 or similar)
- Modified schedules: early release, assemblies, testing weeks

### How schedule shapes pacing
- Block days → 2–3 activities of 20–40 min each, one longer task
- Short periods → 4–6 activities of 5–15 min, tight transitions
- Elementary → full-day arc, not a single lesson

### Calendar interactions
- Quarters/trimesters bookend unit pacing
- Breaks (fall, winter, spring) force unit boundaries
- Testing windows freeze new content delivery
- Teacher workdays / pre-planning days are not instructional

### How the skill uses `parse_calendar.py` output
- Skip non-instructional days when generating week
- Flag week-straddling-break edge cases
- Surface quarter endpoints as natural unit bookends
