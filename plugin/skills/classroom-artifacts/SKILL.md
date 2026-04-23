---
name: classroom-artifacts
description: Generate agenda slides, exit tickets, do-nows, and sub plans from the teacher's active lesson plan. Read the compact plan sidecars when available and fall back to markdown/docx when needed. Do not use for full lesson planning.
---

# Classroom Artifacts

Generate short-form classroom artifacts from an existing lesson plan. The lesson plan is the source of truth for the target day.

## Router

Use this skill for:

- agenda slides
- exit tickets
- do-nows or bell ringers
- sub-ready plans

Do not use this skill for weekly, daily, or unit lesson planning.

## Core rules

1. Source the learning target, agenda, and day structure from the existing plan.
2. Never write student names or PII.
3. Apply the teacher voice where prose exists.
4. Any linked resource must follow the planner's verification rules.
5. Generate artifact prose in Haiku subagents, not in the main session.

## Load discipline

Prefer compact inputs:

- first choice: `.plan.json`
- fallback: `.plan.md`
- last resort: `.docx` with sidecar lookup

Load the voice profile only if the artifact needs prose shaping. Do not load a full weekly plan when only one day is needed.

## Artifact flow

1. Resolve the target day and subject.
2. Load the plan sidecar or markdown for that day.
3. Load `../lesson-planner/references/subagent-roles.md`.
4. Load `references/prompt-contracts/artifact-haiku-json.md`.
5. Use one Haiku subagent to produce the artifact content JSON.
6. Pass plan data and JSON content into the appropriate generator script.

The main session should stitch results and run the generator scripts. It should not draft long artifact text directly.

## Artifact types

### Agenda slide

- Output: one `.pptx` per requested subject/day
- Base template: `assets/agenda-slide-template.pptx`
- Output path: `~/Documents/Lesson Plan Magic/outputs/YYYY-MM-DD_<subject-id>_agenda.pptx`
- Load `references/agenda-slide-patterns.md` only when layout guidance is needed

### Exit ticket

- Output: printable `.docx` or Google Forms-ready `.txt`
- Output path: `~/Documents/Lesson Plan Magic/outputs/YYYY-MM-DD_<subject-id>_exit-ticket.<ext>`
- Load `references/exit-ticket-patterns.md` only when question-writing guidance is needed

### Do-now

- Output: `.docx`
- Output path: `~/Documents/Lesson Plan Magic/outputs/YYYY-MM-DD_<subject-id>_do-now.docx`
- Load `references/do-now-patterns.md` only when prompt-shaping guidance is needed

### Sub plan

- Output: `.docx`
- Output path: `~/Documents/Lesson Plan Magic/outputs/YYYY-MM-DD_<subject-id>_sub-plan.docx`
- Load `references/sub-plan-patterns.md` only when simplification or fallback guidance is needed

## Invocation rules

- If the teacher asks for multiple subjects, iterate and write separate files.
- Do not promise a combined deck or packet unless explicit tooling exists.
- If no plan exists for the target day, ask whether to plan the day first or proceed from a manually supplied learning intention.

## Helper scripts

Each generator accepts:

- `--plan`
- `--date`
- `--subject`
- `--output`
- `--template`
- `--content-file` or `--content-json`
- `--config`
- `--allow-names`

Writes should still flow through the generator scripts so PII checks run before output.

## References

- `references/prompt-contracts/artifact-haiku-json.md`
- `references/agenda-slide-patterns.md`
- `references/exit-ticket-patterns.md`
- `references/do-now-patterns.md`
- `references/sub-plan-patterns.md`
- `../lesson-planner/references/subagent-roles.md`
- `../lesson-planner/references/research-verification.md`

## Tone

Brief, utilitarian, classroom-ready.
