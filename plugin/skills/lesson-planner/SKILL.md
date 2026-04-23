---
name: lesson-planner
description: Generate weekly, daily, or unit lesson plans from the teacher's config, standards, calendar, template, and voice profile. On first run, create or extend ~/Documents/Lesson Plan Magic/config.yaml. Deliver the filled .docx plan plus sidecars. Do not use for agenda slides, exit tickets, do-nows, or sub plans.
---

# Lesson Planner

Generate standards-aligned lesson plans in the teacher's own template, voice, and framework. Never write student names. Never invent citations or standards.

## Router

On every invocation:

1. Check for `~/Documents/Lesson Plan Magic/config.yaml`.
2. If missing, run first-run onboarding.
3. If present, run the planning workflow.

If the teacher names a subject not in config, offer an inline mini-onboarding for that subject instead of failing.

## First-run onboarding

Ask only for what you cannot parse from uploads. Batch questions. Save progress after each major step. Load `references/onboarding.md` before running this flow.

Minimum viable config:

- `teacher.name`, `teacher.state`, `teacher.experience_level`
- At least one subject with `id`, `name`, `schedule`, and either a standards source or an explicit no-standards choice
- Either an uploaded template or a starter template from `assets/starter-templates/`

Past-plans ingest is optional but high-value. `scripts/ingest_past_plans.py` writes both `voice-profile.md` and `voice-profile.json`; keep the markdown human-editable and use the JSON sidecar when you need a compact machine-readable voice summary.

## Planning workflow

### Load discipline

Load only the data needed for this request:

- The relevant subject block from `config.yaml`
- Parsed standards for the target subject
- The target date range from the calendar
- The teacher template metadata
- Voice profile data if present
- Only the framework primers listed in the subject config
- `references/schedule-patterns.md` only if the schedule is ambiguous

Do not load whole reference sets by default. On-demand loading is part of the contract.

### Step 1: Parse the request

Extract:

- scope: `week`, `day`, or `unit`
- subject
- target dates, converted to absolute dates

### Step 2: Ask at most 2-3 clarifying questions

Ask only when unit progress, calendar anomalies, or teacher intent is ambiguous. Batch questions into one turn. If nothing is missing, continue.

### Step 3: Draft in subagents, not the main session

Do not draft long lesson prose in the main session.

- Weekly plan: one Sonnet subagent per instructional day in parallel
- Unit plan: one Sonnet subagent for the unit arc, then one Sonnet subagent per week in parallel
- Single day: one Sonnet subagent

Before delegating, load:

- `references/subagent-roles.md`
- `references/prompt-contracts/day-draft.md`
- any framework primer you will use

Pass only compact context into subagents:

- voice excerpt, not the whole profile
- 1-3 standards with short text, not full parsed JSON
- brief prior-day summary, not the whole week
- calendar anomaly notes only if relevant

### Step 4: Research verification

Only run this step when `defaults.research_depth: verified`.

1. Load `references/research-verification.md`.
2. Load `references/prompt-contracts/research-query-json.md`.
3. Use one Sonnet subagent to propose candidate URLs.
4. Run `scripts/verify_research.py --batch`.

Only cite URLs that verified successfully in this session.

### Step 5: Compliance check

1. Load `references/compliance-checklist.md`.
2. Load `references/prompt-contracts/compliance-json.md`.
3. Use one Haiku subagent for the checklist pass.

Warnings surface to the teacher. Hard-gate failures block output and require fixing the affected day only.

### Step 6: Fill the template

Run `scripts/fill_template.py` with the plan markdown and the chosen template.

- The script writes the final `.docx`
- It also writes `.plan.md` and `.plan.json` sidecars for downstream artifact generation
- On first successful fill, set `subjects[].template.mapping_verified: true`

If a template cell needs light prose reshaping, use Haiku for that cell only.

### Step 7: Optional strict voice polish

Skip unless `defaults.voice_match_level: strict` or the teacher explicitly wants observation-grade polish.

Before delegating, load:

- `references/voice-calibration.md`
- `references/prompt-contracts/voice-polish.md`

Use one Opus subagent. Adjust rhythm/register/warmth only. Do not change content, pedagogy, standards, or URLs.

### Step 8: Deliver

Write the plan to:

`~/Documents/Lesson Plan Magic/outputs/<YYYY-MM-DD>_to_<YYYY-MM-DD>_<subject-id>.docx`

If `defaults.bonus_artifacts_prompt: true`, ask once whether the teacher wants agenda slides, exit tickets, do-nows, or a sub plan.

## Hard rules

1. Never write student names or student PII.
2. Never fabricate citations.
3. Never invent standards codes.
4. Never silently drift from the teacher's template.
5. Never weaken privacy invariants.

## Reference map

Load only what the step needs:

- `references/onboarding.md`
- `references/subagent-roles.md`
- `references/prompt-contracts/day-draft.md`
- `references/prompt-contracts/research-query-json.md`
- `references/prompt-contracts/compliance-json.md`
- `references/prompt-contracts/voice-polish.md`
- `references/voice-calibration.md`
- `references/research-verification.md`
- `references/compliance-checklist.md`
- `references/differentiation.md`
- `references/schedule-patterns.md`
- `references/framework-primers/*.md`

## Scripts

- `scripts/parse_standards.py` — standards source to compact parsed JSON
- `scripts/parse_calendar.py` — calendar source to compact schedule JSON
- `scripts/ingest_past_plans.py` — past plans to `voice-profile.md` plus `voice-profile.json`
- `scripts/verify_research.py` — deterministic URL verification
- `scripts/fill_template.py` — markdown plan plus template to `.docx`, `.plan.md`, and `.plan.json`

Packaged installs auto-bootstrap the pinned Python runtime on first use. Source development uses `pip install -r scripts/requirements-dev.txt`.

## Tone

Utilitarian. Teachers are short on time. Deliver the file, keep wrap-up brief, and ask follow-ups only when needed.
