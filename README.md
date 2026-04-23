<div align="center">

# Jake's Lesson Plan Magic

**An AI planning assistant that writes your lesson plans in your voice,<br>fills your district's template, and hands you a finished Word document.**

<br>

[![Version](https://img.shields.io/badge/version-0.3.4-028090?style=flat-square)](https://github.com/revjake1/lesson-plan-magic/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-028090?style=flat-square)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-028090?style=flat-square)](https://python.org)
[![Works with Cowork](https://img.shields.io/badge/works%20with-Cowork-028090?style=flat-square)](https://claude.ai/cowork)
[![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-028090?style=flat-square)](https://claude.ai)

<br>

[**Install (Cowork)**](#installation--cowork-recommended) · [**Install (Claude Code)**](#installation--claude-code) · [**First-Time Setup**](#first-time-setup) · [**Usage**](#usage) · [**Config Reference**](#configuration-reference) · [**Teacher Guide**](TEACHER_GUIDE.md) · [**FAQ**](#faq)

</div>

---

## What it does

Tell it what you're teaching. Get a finished document — not a wall of text to copy-paste.

The plugin has **two skills** that talk to each other:

| Skill | Trigger | What you get |
|---|---|---|
| **Lesson Planner** | `/lesson-planner` (or plain English in Claude Code) | A filled-in `.docx` lesson plan in your district's template — with real standard codes, learning intentions, differentiation, and verified resource links |
| **Classroom Artifacts** | `/classroom-artifacts` | Agenda slides, exit tickets, do-nows, and sub plans — built from the lesson plan you just generated, or from the saved plan for that day |

Both skills write files to `Documents/Lesson Plan Magic/outputs/`. Generated files stay on your computer unless you choose to share them.

---

## Table of Contents

- [What's in a lesson plan](#whats-in-a-lesson-plan)
- [Classroom artifacts](#classroom-artifacts)
- [Supported instructional frameworks](#supported-instructional-frameworks)
- [Differentiation populations](#differentiation-populations)
- [Before you start](#before-you-start)
- [Installation — Cowork](#installation--cowork-recommended)
- [Installation — Claude Code](#installation--claude-code)
- [First-time setup](#first-time-setup)
- [Usage](#usage)
- [Output files](#output-files)
- [Configuration reference](#configuration-reference)
- [Standards integration](#standards-integration)
- [Voice matching](#voice-matching)
- [Privacy & compliance](#privacy--compliance)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Full teacher guide](#full-teacher-guide)
- [License](#license)

---

## What's in a lesson plan

Every plan includes:

- **Standards** — real codes pulled from your uploaded state standards document or URL, never fabricated. The plugin verifies each code is in your standards source before writing it.
- **Learning intentions and success criteria** — "I am learning… / I can…" on every day, calibrated to your grade level and subject.
- **Instructional framework breakdown** — every activity is labeled with the framework phase it belongs to (e.g., Explore, We Do, Input, Mini-lesson). Supports 10+ frameworks; see [Supported Instructional Frameworks](#supported-instructional-frameworks).
- **Differentiation** — ELL, IEP/504, gifted, and tiered readiness, always at the accommodation level — never by student name. FERPA-safe by design.
- **Evidence of learning** — specific look-fors and checkpoints the teacher can use during instruction.
- **Materials list** — automatically derived from the planned activities.
- **Verified resource links** — every link is confirmed live and relevant before it appears in your plan. Unverified resources are described in plain English, never written as a fake hyperlink.

Plans come out as filled `.docx` files in your district's template. Open in Word or upload to Google Docs.

---

## Classroom artifacts

The `/classroom-artifacts` skill pulls content from your saved lesson plan for that day — you never have to retype a learning intention or activity.

| Artifact | Example request | Output format |
|---|---|---|
| **Agenda slide** | `Agenda slide for today.` | `.pptx` — a single slide for the requested subject/day, with learning intention, success criteria, and agenda bullets |
| **Exit ticket** | `Exit ticket for Chemistry.` | `.docx` half-sheet for printing, or `.txt` optimized for Google Forms copy-paste — 2–3 content questions, one metacognitive prompt, optional extension |
| **Do-now / bell ringer** | `Do-now for tomorrow.` | `.docx` — self-explanatory prompt students can start independently with no teacher setup |
| **Sub plan** | `Sub plan for Friday — I'm out sick.` | `.docx` — attendance procedure, activity, materials, backup plan, and emergency contact section |

All artifacts scan for student PII before saving. The sub plan template uses fictional sample contacts — replace them with real ones after generation.

---

## Supported instructional frameworks

Tell the plugin which framework(s) you use during setup, and every activity in your lesson plan will be labeled with the correct phase name. Mix frameworks across subjects.

| Framework | Label style in plan |
|---|---|
| **5E** (Engage, Explore, Explain, Elaborate, Evaluate) | `Engage:`, `Explore:`, `Explain:`, `Elaborate:`, `Evaluate:` |
| **Gradual Release** (I Do / We Do / You Do) | `I Do:`, `We Do:`, `You Do:` |
| **Workshop Model** | `Mini-lesson:`, `Independent Practice:`, `Share:` |
| **SIOP** (Sheltered Instruction Observation Protocol) | `Building Background:`, `Interaction:`, `Review/Assessment:` |
| **UDL** (Universal Design for Learning) | `Representation:`, `Action & Expression:`, `Engagement:` |
| **Direct Instruction** | `Anticipatory Set:`, `Instruction:`, `Guided Practice:`, `Independent Practice:`, `Closure:` |
| **Project-Based Learning (PBL)** | `Driving Question:`, `Inquiry:`, `Creation:`, `Critique & Revision:`, `Presentation:` |
| **Hattie's Visible Learning** | `Success Criteria:`, `Direct Instruction:`, `Feedback:`, `Spaced Practice:` |
| **Marzano** | `Setting Objectives:`, `New Knowledge:`, `Practice:`, `Hypothesis Testing:` |
| **SWIRL** | `See:`, `Write:`, `Inquire:`, `Read:`, `Listen:` |
| **Custom framework** | Your district's own framework — upload the guide and the plugin learns the phase names |

---

## Differentiation populations

During setup, choose which populations to differentiate for in every plan. The plugin writes accommodation notes at the population level — never by student name.

| Population tag | Config value | What appears in the plan |
|---|---|---|
| **ELL** | `ELL` | Language scaffolds, sentence frames, visual supports, vocabulary front-loading |
| **IEP accommodations** | `SPED_IEP` | Extended-time notes, reduced-distraction alternatives, chunked directions, preferential seating suggestions |
| **504 accommodations** | `SPED_504` | Same accommodation language as IEP notes, scoped to 504 plans |
| **Gifted** | `GIFTED` | Extension prompts, above-grade-level resources, choice boards, independent project options |
| **Tiered readiness** | Use `tiers: [novice, on-level, advanced]` (or `[on-level, extension]`) | 2–3 readiness tiers with different entry points for the same activity |

You can enable any combination. If you need a population not listed, describe it during setup.

If you ask for artifacts across multiple subjects, the plugin generates one file per subject rather than a combined deck or packet.

---

## Before you start

**Required:**
- **Python 3.9 or newer** — on Mac, open Terminal and type `python3 --version`. On Windows, open Command Prompt and type `python --version`. If Python isn't installed, download it free at [python.org](https://python.org).
- **A Cowork or Claude Code account** — sign up free at [claude.ai](https://claude.ai).
- **The plugin file** — `jakes-lesson-plan-magic.plugin` — download from [Releases](https://github.com/revjake1/lesson-plan-magic/releases).

**Highly recommended (collect before setup):**
- Your **district lesson plan template** — the `.docx` Word file your school requires. Ask your instructional coach if you don't have it.
- Your **state standards** — a PDF of your state standards document, a URL to your state's standards page, or pasted text. The plugin indexes them locally; no standards are sent anywhere.
- A **folder of past lesson plans** — even 5–10 old `.docx` files help. The plugin reads them to learn your voice, your density, and your go-to activity types.
- Your **school calendar** — an `.ics` file exported from Google Calendar or Outlook, or a PDF with selectable text from your district website.
- Your **school calendar** — an `.ics` file exported from Google Calendar or Outlook, or a PDF with selectable text from your district website. Lets the plugin automatically skip holidays, testing days, and half-days.

---

## Installation — Cowork (Recommended)

Cowork is a free desktop app with a built-in plugin installer. It's the right choice for most teachers.

### Step 1 — Download and install Cowork

Get the free desktop app at [claude.ai/cowork](https://claude.ai/cowork) and install it like any Mac or Windows app.

### Step 2 — Install the plugin

1. Download `jakes-lesson-plan-magic.plugin` from [Releases](https://github.com/revjake1/lesson-plan-magic/releases).
2. Open Cowork.
3. Drag and drop the `.plugin` file into the Cowork window. A preview card appears.
4. Click **Accept**. Two new skills appear: `/lesson-planner` and `/classroom-artifacts`.

### Step 3 — Make sure Python is installed

Lesson Plan Magic needs **Python 3.9 or newer** on your computer, but you do **not** need to install its helper libraries by hand anymore. On first use, the plugin installs its own pinned Python helpers automatically into your Lesson Plan Magic folder.

That first helper install may take a minute or two and needs normal internet access.

If the automatic helper install cannot finish, the plugin prints plain-English next steps. In practice that usually means one of three things: Python itself is missing, the machine cannot reach PyPI on first run, or the host app cannot write to `Documents/Lesson Plan Magic/`.

### Step 4 — Add your school calendar (optional, highly recommended)

Export an `.ics` file from Google Calendar or Outlook, or upload a PDF with selectable text from your district website. Upload it during setup, or later by saying `Update my config.` Once loaded, the plugin can skip breaks and account for testing days or half-days when sequencing plans. Scanned-image PDFs usually won't parse reliably.

### Step 5 — Start your first planning session

Type `/lesson-planner` in the Cowork chat. If it's your first time, the plugin walks you through a **10–20 minute setup conversation** — your name, subjects, standards, schedule, and framework. You can drop files at any point. Progress saves after every step, so interruptions are fine.

> **Tip:** In Cowork, type `/` at any time to see all available skills.

---

## Installation — Claude Code

Use this if you're already running Claude Code or your IT department has set it up for you.

1. Download `jakes-lesson-plan-magic.plugin` from [Releases](https://github.com/revjake1/lesson-plan-magic/releases).
2. Open Claude Code and go to **Settings → Plugins**.
3. Click **Install from file** and select the `.plugin` file. Enable it from the plugin list.
4. Make sure Python 3.9+ is installed. The plugin installs its own helper libraries automatically on first use.
5. Just talk in plain English — `Plan my week for Chemistry` — the plugin recognizes planning requests automatically. No slash command needed.

---

## First-time setup

The first time you trigger the lesson planner, it starts a guided conversation. You only do this once per installation.

<details>
<summary><strong>What setup covers (click to expand)</strong></summary>

| Step | What it asks | Notes |
|---|---|---|
| 1 | Your name, state, and school | Plain English — no specific format required |
| 2 | Experience level | New teacher (0–3 yrs), Mid-career (3–10), Veteran (10+), or Veteran-new-to-subject. Affects how much pedagogy jargon appears in your plans. |
| 3 | Your subjects / preps | One entry per prep. Elementary teachers: enter one "subject" (e.g., "3rd Grade") with content areas (math, reading, science, etc.) inside it. |
| 4 | Per-subject setup | Standards source, district template, schedule type, instructional framework(s), and differentiation populations — collected in one message per subject, not nine separate questions. |
| 5 | Past plans _(optional)_ | Drop a folder of old `.docx` plans. The plugin reads them to learn your voice, density, and activity preferences. Even 5–10 old plans make a significant difference. |
| 6 | School calendar _(optional)_ | Upload an `.ics` calendar or a PDF with selectable text. Holidays, test days, and half-days are skipped automatically from that point forward. |

At the end, the plugin writes a `config.yaml` file to `Documents/Lesson Plan Magic/` and gives you a plain-English summary of everything it learned.

</details>

<details>
<summary><strong>Schedule types supported (click to expand)</strong></summary>

| Schedule type | Description |
|---|---|
| `block` | 90-minute block periods, typically 4 per day |
| `bell` | 5–7 shorter periods per day (45–55 min typical) |
| `elementary` | Full-day self-contained with multiple content areas |
| `ab-rotation` | Alternating A-day / B-day block schedule |
| `custom` | Any other pattern — describe it in plain English |

</details>

---

## Usage

### Lesson plans

```
Plan my week for Chemistry.
Plan next week for AP Chemistry.
Make a daily plan for Friday in Algebra.
I need a polished plan for Thursday — my principal is observing.
Plan the next three weeks of American Literature, ending with a Socratic seminar.
Plan my week.                          ← elementary: covers all content areas in one plan
We had a fire drill. Re-plan Friday.
What should I teach next week? We just finished the Civil War unit.
Plan next week for all my preps.
I want to start the photosynthesis unit Monday — plan the whole unit.
```

The plugin may ask 2–3 clarifying questions in a single message, then runs each day in parallel — a full weekly plan does not take five times as long as a single day.

### Classroom artifacts

```
Agenda slide for today.
Agenda slides for all my subjects today.
Exit ticket for Chemistry.
Exit ticket for Thursday — Google Forms format.
Do-now for tomorrow's Algebra.
Bell ringer that spirals back to last week's vocabulary.
Sub plan for tomorrow — I'm out sick.
Sub plan for Friday, just Chemistry 3rd period.
```

### Updating your settings

```
Update my config.
Add a new subject — I'm picking up Geometry next semester.
I switched to a new district template. How do I upload it?
Change my voice match level to strict — I have a big observation coming up.
Add "Ms. Rodriguez" to my approved names list.
Upload new standards for AP Chemistry.
I have a new school calendar to upload.
Resume my setup.
```

---

## Output files

All files go to one folder:

| Platform | Path |
|---|---|
| Mac / Linux | `~/Documents/Lesson Plan Magic/outputs/` |
| Windows | `%USERPROFILE%\Documents\Lesson Plan Magic\outputs\` |

Typical filenames are date/subject based. The exact stem for daily vs. unit plans can vary by scope:

```
2026-04-21_to_2026-04-25_chem.docx          ← weekly lesson plan
2026-04-25_chem.docx                          ← daily lesson plan
unit_2026-04-21_to_2026-05-08_amer-lit.docx  ← unit plan
2026-04-21_chem_agenda.pptx                  ← agenda slide
2026-04-21_chem_exit-ticket.docx             ← exit ticket (printable)
2026-04-21_chem_exit-ticket.txt              ← exit ticket (Google Forms format)
2026-04-22_chem_do-now.docx                  ← do-now / bell ringer
2026-04-24_chem_sub-plan.docx                ← sub plan
```

Every lesson plan also writes a **`.plan.md` sidecar file** alongside the `.docx`. The classroom-artifacts skill reads this sidecar to pull learning intentions, activities, and standards without opening the Word document.

Double-click any `.docx` to open in Word or Google Docs. Double-click any `.pptx` for PowerPoint or Google Slides.

For lesson plans, the plugin also saves a `.plan.md` sidecar next to the `.docx`; that sidecar is what the classroom-artifacts skill reuses later. The helper scripts refuse to write outside `Documents/Lesson Plan Magic/outputs/` unless you explicitly override that fence.

Current limits in `v0.3.4`: no PDF export, no native Google Forms creation, and no direct LMS posting. Exit tickets can produce Google Forms-ready `.txt`, but the actual form or LMS post is still manual.

---

## Configuration reference

The plugin stores all your settings in one file:

| Platform | Location |
|---|---|
| Mac / Linux | `~/Documents/Lesson Plan Magic/config.yaml` |
| Windows | `%USERPROFILE%\Documents\Lesson Plan Magic\config.yaml` |

You can edit this file directly, or say `Update my config` to let the plugin walk you through changes.

<details>
<summary><strong>Full config structure (click to expand)</strong></summary>

```yaml
version: "0.3.4"

teacher:
  name: "Ms. Hallman"
  experience_level: veteran      # new | mid-career | veteran | new-to-subject
  state: "GA"
  school: "Statesboro High"
  district: "Bulloch County Schools"

subjects:
  - id: chem
    name: "Chemistry"
    subject_type: departmentalized   # departmentalized | elementary-self-contained | co-taught

    standards:
      - path: ~/Documents/Lesson Plan Magic/standards/ga-science-standards.pdf
      # or: url: https://...
      # or: inline: "CHEM.1 Matter and its interactions..."

    template:
      path: ~/Documents/Lesson Plan Magic/templates/bulloch-weekly-block.docx
      mapping_verified: true

    schedule:
      type: block              # block | bell | elementary | ab-rotation | custom
      period_length_minutes: 90
      days: [M, T, W, R, F]
      periods_per_day: 1

    frameworks:
      - 5e
      - gradual-release
      # supported: 5e, gradual-release, workshop-model, siop, udl, direct-instruction,
      #            project-based, hattie, marzano, swirl
      # custom: set custom_framework_path instead

    differentiation:
      populations: [ELL, SPED_IEP, GIFTED]
      tiers: [novice, on-level, advanced]

    voice_profile: ~/Documents/Lesson Plan Magic/voice/chem_voice.md
    past_plans_dir: ~/Documents/Lesson Plan Magic/past-plans/chem/

    pacing:
      scope_and_sequence: ~/Documents/Lesson Plan Magic/scope/chem-scope.md
      last_planned_week_end: "2026-04-18"
      current_unit: "Stoichiometry"

defaults:
  output_formats: [docx]       # v0.3.4 ships docx only; pdf is on the roadmap
  research_depth: verified     # off | generic-queries | verified
  compliance_mode: soft-warn   # strict | soft-warn | off
  voice_match_level: calibrated  # generic | calibrated | strict
  bonus_artifacts_prompt: true
  calendar_path: "calendar/2025-26.ics"

privacy:
  student_data: never          # hard-coded — not user-configurable
  telemetry: off               # hard-coded — not user-configurable
  pii_scan_before_write: true  # hard-coded — not user-configurable
  retention_days: 365          # advisory only; not auto-enforced by the plugin

approved_names:
  - "Ms. Rodriguez"            # teacher.name and co_teacher_name are auto-allowlisted;
  - "Mr. Chen"                 # add historical figures or other staff here as needed
```

</details>

### Config fields explained

| Field | What it controls |
|---|---|
| `experience_level` | How much pedagogy vocabulary appears in plans. `new` means more scaffolding, `veteran` means leaner prose. Valid values: `new` \| `mid-career` \| `veteran` \| `new-to-subject`. |
| `subject_type` | `departmentalized` = single subject; `elementary-self-contained` = full day with content areas inside; `co-taught` = two teachers, split-instruction differentiation. |
| `frameworks` | One or more framework IDs per subject. Activities in plans are labeled with that framework's phase names. |
| `research_depth` | `off` = no external links; `generic-queries` = suggests resources without live link verification; `verified` = every link checked live before inclusion. |
| `voice_match_level` | `generic` = no voice matching; `calibrated` = uses voice profile loosely; `strict` = maximally faithful to past-plan voice. |
| `compliance_mode` | How strictly to enforce the compliance checklist. `strict` blocks delivery on violations; `soft-warn` delivers with warnings at the top (default); `off` skips checking entirely. |
| `approved_names` | Names the PII scanner passes through. The teacher's own name and any co-teacher name are auto-allowlisted. Add historical figures or other staff here. Student names must never appear here. |

---

## Standards integration

The plugin builds a local index of your standards on first use and updates it when you upload a new standards document. It never fabricates standard codes.

**What it can read:**
- PDF files (state standards documents, curriculum guides)
- URLs pointing to standards pages
- Pasted plain text

**How it works:**

1. You upload your standards source during setup (or later with `Upload new standards for [subject]`).
2. The plugin parses the document with `parse_standards.py` and builds a local JSON index.
3. When generating a plan, it searches that index for codes that match the planned content — fuzzy matching handles minor wording differences.
4. If no matching standard is found, the plan flags it in the compliance notes rather than inventing a code.

**To update standards:**

```
Upload new standards for Chemistry.
My state just released updated standards — can you re-index them?
```

---

## Voice matching

Voice matching lets the plugin write in your style — your sentence length, your warmth, your go-to activity verbs, your level of detail.

**How it works:**

1. During setup (or later with `Update my config`), you point the plugin at a folder of past `.docx` lesson plans.
2. `ingest_past_plans.py` reads those plans and extracts style signals: sentence density, vocabulary richness, activity type frequencies, warmth markers, formality level.
3. That profile is saved to a local `.json` file.
4. When generating a new plan, the profile is loaded and used to calibrate the output.

**Voice match levels:**

| Level | Behavior |
|---|---|
| `generic` | No voice matching — standard professional tone |
| `calibrated` | Voice profile used as a loose guide; may diverge for pedagogical clarity |
| `strict` | Voice profile followed as closely as possible; best for observation prep |

**If the output doesn't sound like you:**

```
The output doesn't sound like me — can you adjust the voice?
Set my voice match level to strict.
I want to upload more past plans to improve the voice matching.
```

The more past plans you provide, the better the match. Aim for at least 10–15 plans across different units for `strict` mode.

---

## Privacy & compliance

Four guarantees — hard-coded, not user-configurable:

| Guarantee | What it means |
|---|---|
| **Never writes student names** | Differentiation always uses population language: "students with extended-time accommodations" — never a student's name. FERPA-safe by design. |
| **PII scan before every save** | Every `.docx`, `.pptx`, and `.txt` file is scanned for names, SSNs, phone numbers, email addresses, student IDs, IEP phrasing, and medical notes before it's written to disk. If something is found, the file is not saved and you see a plain-English explanation. |
| **No plugin telemetry or hosted storage** | Generated files stay local and `privacy.telemetry: off` is hard-coded. The plugin makes normal outbound web requests only when verifying resource links or fetching standards URLs — both initiated from your machine. |
| **Never fabricates citations** | Every link is verified as live and accurate before inclusion. Unverified resources are described in plain English — never written as a broken or made-up hyperlink. |

Lesson Plan Magic runs inside Cowork or Claude Code, so your planning conversation follows the normal privacy and security model of that host app.

**FERPA note:** The plugin is designed for teacher use only. It should not receive individually identifiable student information. Differentiation notes reference accommodation populations (ELL, IEP/504, gifted), not individual students.

---

## Troubleshooting

<details>
<summary><strong>Python tools aren't installing</strong></summary>

If `pip install` fails:
- Try `pip3 install ...` instead of `pip`
- On Windows, try `python -m pip install ...`
- If you get a permissions error on Mac, try `pip3 install --user ...`
- Make sure Python 3.9+ is installed: `python3 --version`

</details>

<details>
<summary><strong>The plugin isn't recognized in Cowork</strong></summary>

- Make sure you clicked **Accept** after dragging the `.plugin` file in.
- Try closing and reopening Cowork.
- Re-download the `.plugin` from [Releases](https://github.com/revjake1/lesson-plan-magic/releases) and re-install — a partial download can cause this.

</details>

<details>
<summary><strong>The output doesn't use my district template</strong></summary>

During setup, when the plugin asks for your template, drop the `.docx` file directly into the chat. If you already completed setup, say: `I have a new district template to upload.`

If the template has locked or form-field placeholders, the plugin may fall back to a built-in template. Try `unlocking` the Word document before uploading (Word → Review → Restrict Editing → Stop Protection).

</details>

<details>
<summary><strong>Standard codes are missing or wrong</strong></summary>

- Make sure you uploaded your standards document during setup.
- Say `Upload new standards for [subject]` to re-index.
- If codes still look wrong, try uploading a PDF directly from your state education department's website.

</details>

<details>
<summary><strong>The plan doesn't skip my school's holidays</strong></summary>

You may not have uploaded your school calendar. Say `I have a school calendar to upload.` and drop an `.ics` or PDF file. Then say `Re-plan next week` to regenerate.

</details>

<details>
<summary><strong>I got interrupted during setup</strong></summary>

Say `Resume my setup` — progress is saved automatically after every step.

</details>

<details>
<summary><strong>PII scan blocked my file</strong></summary>

The plan contained something that matched the PII scanner's patterns. Review the explanation the plugin gives you. Common causes:
- A co-teacher's name that isn't in your `approved_names` list — say `Add [name] to my approved names list`.
- Fictional sample contacts in a sub plan — replace them after generating the document.
- A standards code that looks like a phone number — contact the developer via [Issues](https://github.com/revjake1/lesson-plan-magic/issues).

</details>

---

## FAQ

<details>
<summary>Do I need a Claude.ai account?</summary>

Yes — both Cowork and Claude Code run on Anthropic's Claude AI. Sign up free at [claude.ai](https://claude.ai). A paid plan is not required to get started.

</details>

<details>
<summary>What if I don't have my district's lesson plan template?</summary>

Choose one of three built-in starter templates during setup:
- **Weekly block** — 90-minute block periods
- **Weekly bell** — 5–7 period bell schedule
- **Daily one-pager** — single-day, single-subject

You can swap in your real district template at any time by saying `I have a new district template to upload.`

</details>

<details>
<summary>What if I don't have my state standards?</summary>

The plugin still works — it skips the standard-code step and flags it in the compliance notes at the top of your plan. Add standards any time: `Upload new standards for [subject].`

</details>

<details>
<summary>Can elementary teachers use this?</summary>

Yes. Self-contained classrooms are fully supported. Set up one "subject" (e.g., "3rd Grade") with content areas inside — math, reading, writing, science, social studies. The plugin generates one cohesive plan covering your whole day.

</details>

<details>
<summary>Can I use this for co-taught classes?</summary>

Yes. During setup, say the class is co-taught and give your co-teacher's name and role. Differentiation sections will include suggestions for splitting the instructional work between you. Add your co-teacher's name to `approved_names` so the PII scanner doesn't flag it.

</details>

<details>
<summary>The output doesn't sound like me.</summary>

Make sure you uploaded past plans during setup — voice matching gets dramatically better with even 5–10 old Word documents. If it still sounds off: `The output doesn't sound like me — can you adjust the voice?` Or: `Set my voice match level to strict.`

</details>

<details>
<summary>I got interrupted during setup. How do I resume?</summary>

Just say `Resume my setup` — progress is saved automatically after every step.

</details>

<details>
<summary>I teach three sections of the same class. Does the plan cover all of them?</summary>

Yes. During setup (or via `Update my config`), tell it you have multiple sections. The plugin accounts for scheduling differences between sections.

</details>

<details>
<summary>Can it post directly to Google Classroom or Canvas?</summary>

Not in this version — LMS integration is on the roadmap. Upload output files manually for now.

</details>

<details>
<summary>Does it support AP or IB courses?</summary>

Yes — just reference your AP/IB standards during setup. The plugin supports any text-based standards document. For AP, College Board publishes course and exam descriptions as PDFs; upload one of those.

</details>

<details>
<summary>Can I use my own instructional framework that isn't on the supported list?</summary>

Yes. During setup, say "I use a custom framework" and upload your district's framework guide. The plugin learns the phase names from the document.

</details>

<details>
<summary>Will it work with block schedule A/B rotation?</summary>

Yes. Choose `ab-rotation` as your schedule type during setup. Plans respect the rotation and only plan activities for days that period meets.

</details>

<details>
<summary>Where does the plugin store my files?</summary>

All output files go to `Documents/Lesson Plan Magic/outputs/` on your machine. Your `config.yaml` and supporting files (standards index, voice profile, parsed calendar) live in `Documents/Lesson Plan Magic/`. Nothing is uploaded to external storage.

</details>

---

## Full teacher guide

For complete documentation including worked examples, framework walkthroughs, configuration details, and troubleshooting for specific scenarios, see **[TEACHER_GUIDE.md](TEACHER_GUIDE.md)**.

---

## License

MIT — see [LICENSE](LICENSE).

*Jake's Lesson Plan Magic · v0.3.4 · [jakehallman.com](https://jakehallman.com)*
