# Onboarding — first-run runtime script

Runs once per teacher. Batch questions by topic — don't ask nine things in a row. Save progress after each numbered step so a dropped session isn't lost.

## Step 1 — Greet + scope

> "I'll help you set up Lesson Plan Magic. Takes 10-20 minutes depending on how much you upload. You can drop files at any point or answer in chat. Let's start: your name, state, and school?"

## Step 2 — Experience

Ask which fits best:

- New (0-3 years) — plain language, explain frameworks inline
- Mid-career (3-10) — normal pedagogy vocab
- Veteran (10+) — dense vocab, terse explanations
- Veteran, new to subject — normal vocab, offer content-area scaffolding

Store as `teacher.experience_level`. Later prose calibrates to this.

## Step 3 — Subject inventory

> "How many preps do you have, and what are they? ('Chemistry I and AP Chemistry,' or '4th grade all subjects.')"

Elementary self-contained → ONE subject with multiple `content_areas` inside (see `../../../shared/config-schema.md`). Secondary → one subject per prep.

## Step 4 — Per-subject loop

For each subject, ask in ONE batched message:

1. **Standards** — "Upload state standards PDF, paste a URL, or paste text. Or skip — we'll run with no standards and warn at compliance check."
2. **Template** — "Upload your district lesson-plan template (.docx). Or pick a starter: weekly-block / weekly-bell / daily-one-pager."
3. **Schedule** — "45-min periods five days? 90-min block? A/B rotation? Elementary all-day?"
4. **Frameworks** — "Any pedagogy framework? (SWIRL, UDL, 5E, SIOP, gradual-release, workshop, direct instruction, project-based, Marzano, Hattie, or none.) You can upload a district framework doc too."
5. **Differentiation** — "Which apply to this group? Tiered (novice/on-level/advanced), ELL, SPED/IEP, 504, gifted."

Record answers to `subjects[].*` in config.

## Step 5 — Past plans (optional but high-value)

> "Drop a folder of past lesson plans if you have any. I'll extract your layout, voice, favorite activities, and pacing. More plans = better voice match. Skip if you don't have any."

If provided: run `scripts/ingest_past_plans.py <folder>`. Writes `past-plans/<subject-id>/voice-profile.md` and sets `subjects[].voice_profile`.

## Step 6 — Voice calibration (3 quick questions)

Even with past plans, confirm:

1. **Script vs. outline** — "Plans closer to a word-by-word script, or bullets you fill in live?"
2. **Core model** — "Direct instruction / inquiry / workshop / project-based / mix / tell me each time."
3. **Warmth** — "Personality in plans (humor, asides, 'kids will groan at this') or clinical?"

If past-plans analysis already answered these, CONFIRM don't re-ask. Store answers in the voice profile.

## Step 7 — School calendar

> "Upload your school-year calendar (.ics from Google/Outlook, or PDF). I'll know about holidays, testing, half days, PD days automatically."

Store as `calendar/<year>.ics` (or `.pdf`). Set `defaults.calendar_path`.

## Step 8 — LMS + output prefs

- "Post to an LMS? (Google Classroom / Canvas / Schoology / none — v0.1 outputs copy-paste text only.)"
- "Output formats? (.docx filled template is always produced; PDF is on the roadmap (planned for v0.3). Google Doc export planned for a later release.)"

## Step 9 — Confirm

Write `config.yaml`. Show summary in plain English:

> "All set. I'll plan: Chemistry, AP Chemistry. Standards: OH NGSS + College Board AP. Template: your district Word doc. Framework: 5E + gradual-release. Voice: learned from 18 past plans. Try 'plan Chemistry for next week.'"

## Skip discipline

Any optional step can be skipped by typing "skip" or "later". Set `onboarding.incomplete: true` and re-prompt on the next run until the field is filled. Never block a first planning request on optional fields.

## Progress-save points

After steps 3, 4 (per subject), 5, 6, 7, and 9. A dropped session resumes from the last save point.
