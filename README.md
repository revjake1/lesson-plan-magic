<div align="center">

# Jake's Lesson Plan Magic

**An AI planning assistant that writes your lesson plans in your voice,<br>fills your district's template, and hands you a finished Word document.**

<br>

[![Version](https://img.shields.io/badge/version-0.2.5-028090?style=flat-square)](https://github.com/revjake1/lesson-plan-magic/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-028090?style=flat-square)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-028090?style=flat-square)](https://python.org)
[![Works with Cowork](https://img.shields.io/badge/works%20with-Cowork-028090?style=flat-square)](https://claude.ai/cowork)
[![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-028090?style=flat-square)](https://claude.ai)

<br>

[**Install (Cowork)**](#installation--cowork-recommended) · [**Install (Claude Code)**](#installation--claude-code) · [**Usage Examples**](#using-it) · [**Teacher Guide**](TEACHER_GUIDE.md) · [**FAQ**](#faq)

</div>

---

## What it does

Tell it what you're teaching. Get a finished document — not a wall of text to copy-paste.

The plugin has **two skills** that talk to each other:

| Skill | Trigger | What you get |
|---|---|---|
| **Lesson Planner** | `/lesson-planner` | A filled-in `.docx` lesson plan in your district's template — with real standard codes, learning intentions, differentiation, and verified resource links |
| **Classroom Artifacts** | `/classroom-artifacts` | Agenda slides, exit tickets, do-nows, and sub plans — all pulled from your existing lesson plan automatically |

Both output to `Documents/Lesson Plan Magic/outputs/` on your computer. No cloud storage. No sharing. Files are yours.

---

## What's in a lesson plan

Every plan includes:

- **Standards** — real codes pulled from your uploaded state standards, never fabricated
- **Learning intentions and success criteria** — "I am learning… / I can…" on every day
- **Instructional framework** — 5E, gradual release, workshop model, SWIRL, SIOP, UDL, direct instruction, PBL, or your district's custom framework
- **Differentiation** — ELL, IEP/504, gifted, and tiered readiness, written at the accommodation level — never by student name
- **Evidence of learning** — what to look for during instruction
- **Verified resource links** — every link is confirmed live before it appears in your plan

Plans come out as filled `.docx` files in your district's template. Open them in Word or Google Docs.

---

## What classroom artifacts look like

| Artifact | Example request | Output |
|---|---|---|
| **Agenda slide** | `Agenda slide for today.` | `.pptx` — learning intention, success criteria, and agenda bullets, one slide per subject |
| **Exit ticket** | `Exit ticket for Chemistry.` | `.docx` half-sheet — 2–3 content questions, one metacognitive prompt, optional extension |
| **Do-now / bell ringer** | `Do-now for tomorrow.` | `.docx` — self-explanatory, students start independently, no teacher setup required |
| **Sub plan** | `Sub plan for tomorrow — I'm out sick.` | `.docx` — attendance procedure, activity, materials, backup plan, emergency contacts |

---

## Before you start

**Required:**
- **Python 3.9 or newer** — on Mac, open Terminal and type `python3 --version`. On Windows, open Command Prompt and type `python --version`. If Python isn't installed, download it free at [python.org](https://python.org).
- **A Cowork or Claude Code account** — sign up free at [claude.ai](https://claude.ai).
- **The plugin file** — `jakes-lesson-plan-magic.plugin` (see [Releases](https://github.com/revjake1/lesson-plan-magic/releases))

**Highly recommended (collect before setup):**
- Your **district lesson plan template** — the `.docx` Word file your school requires. Ask your instructional coach if you don't have it.
- Your **state standards** — a PDF, a URL to your state's standards page, or pasted text.
- A **folder of past lesson plans** — even 5–10 old `.docx` files. The plugin reads them to learn your voice, your density, your go-to activities. The more you give it, the more it sounds like you.
- Your **school calendar** — an `.ics` file exported from Google Calendar or Outlook, or a PDF from your district's website.

---

## Installation — Cowork (Recommended)

Cowork is a free desktop app with a built-in plugin installer and a cleaner interface. It's the right choice for most teachers.

### Step 1 — Download and install Cowork

Get the free desktop app at [claude.ai/cowork](https://claude.ai/cowork) and install it like any Mac or Windows app.

### Step 2 — Install the plugin

1. Download `jakes-lesson-plan-magic.plugin` from [Releases](https://github.com/revjake1/lesson-plan-magic/releases).
2. Open Cowork.
3. Drag and drop the `.plugin` file into the Cowork window. A preview card appears.
4. Click **Accept**. Done — two new skills appear: `/lesson-planner` and `/classroom-artifacts`.

### Step 3 — Install Python tools (one-time)

Open **Terminal** (Mac) or **Command Prompt** (Windows) and paste:

```
pip install python-docx python-pptx pypdf requests beautifulsoup4 rapidfuzz pyyaml
```

Wait for it to finish — text will scroll by, that's normal. If you see "pip not found," try `pip3` instead.

### Step 4 — Connect your calendar (optional, highly recommended)

In Cowork: click **Connectors** in the sidebar → find **Google Calendar** or **Microsoft Outlook Calendar** → click **Connect**. Once connected, the plugin automatically skips holidays, testing days, and half-days without you having to mention them.

You can also connect Gmail or Outlook if you want the plugin to reference upcoming events when writing sub plans.

### Step 5 — Start your first planning session

Type `/lesson-planner` in the Cowork chat. If it's your first time, the plugin walks you through a **10–20 minute setup conversation** — your name, subjects, standards, schedule, and framework. Drop files at any point. Progress saves after every step, so interruptions are fine.

> **Tip:** In Cowork, type `/` at any time to see all available skills.

---

## Installation — Claude Code

Use this if you're already running Claude Code or your IT department has set it up for you.

1. Download `jakes-lesson-plan-magic.plugin` from [Releases](https://github.com/revjake1/lesson-plan-magic/releases).
2. Open Claude Code and go to **Settings → Plugins**.
3. Click **Install from file** and select the `.plugin` file. Enable it from the plugin list.
4. Install Python tools — same command as above:
   ```
   pip install python-docx python-pptx pypdf requests beautifulsoup4 rapidfuzz pyyaml
   ```
5. Just talk in plain English — `Plan my week for Chemistry` — the plugin recognizes planning requests automatically. No slash command needed.

---

## First-time setup

The first time you trigger the lesson planner, it starts a guided conversation. You only do this once.

<details>
<summary><strong>What setup covers (click to expand)</strong></summary>

| Step | What it asks | Notes |
|---|---|---|
| 1 | Your name, state, and school | Plain English |
| 2 | Experience level | New (0–3 yrs), Mid-career (3–10), Veteran (10+), or Veteran-new-to-subject. Affects how much pedagogy jargon appears in your plans. |
| 3 | Your subjects / preps | One entry per prep. Elementary teachers: one "subject" with content areas inside. |
| 4 | Per-subject setup | Standards, district template, schedule, instructional framework, and differentiation populations — all in one message per subject, not nine separate questions. |
| 5 | Past plans _(optional)_ | Drop a folder of old `.docx` plans. The plugin learns your voice from them. Even 5–10 makes a huge difference. |
| 6 | School calendar _(optional)_ | Upload an `.ics` or PDF calendar, or use your Cowork Connector. Holidays and test days skip automatically. |

At the end, the plugin writes a `config.yaml` to your Documents folder and gives you a plain-English summary of everything it learned.

</details>

---

## Using it

### Lesson plans

```
Plan my week for Chemistry.
Plan next week for AP Chemistry.
Make a daily plan for Friday in Algebra.
I need a polished plan for Thursday — my principal is observing.
Plan the next three weeks of American Literature, ending with a Socratic seminar.
Plan my week.                          ← elementary: covers all content areas
We had a fire drill. Re-plan Friday.
What should I teach next week? We just finished the Civil War unit.
```

The plugin may ask 2–3 clarifying questions in a single message, then runs each day in parallel — a full weekly plan doesn't take five times as long as a single day.

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
```

---

## Output files

All files go to one folder:

| Platform | Path |
|---|---|
| Mac / Linux | `Documents/Lesson Plan Magic/outputs/` |
| Windows | `Documents\Lesson Plan Magic\outputs\` |

Files are named by date and subject:

```
2026-04-21_to_2026-04-25_chem.docx       ← weekly plan
2026-04-25_chem.docx                      ← daily plan
unit_2026-04-21_to_2026-05-08_amer-lit.docx  ← unit plan
2026-04-21_chem_agenda.pptx              ← agenda slide
2026-04-21_chem_exit-ticket.docx         ← exit ticket
2026-04-22_chem_do-now.docx              ← do-now
2026-04-24_chem_sub-plan.docx            ← sub plan
```

Double-click any `.docx` to open in Word or Google Docs. Double-click any `.pptx` for PowerPoint or Google Slides.

---

## Privacy

Four guarantees — hard-coded, not configurable:

| Guarantee | What it means |
|---|---|
| **Never writes student names** | Differentiation always uses population language: "students with extended-time accommodations" — never a student's name. FERPA-safe by design. |
| **PII scan before every save** | Every file is scanned for names, SSNs, phone numbers, email addresses, student IDs, IEP phrasing, and medical notes before it's written to disk. If something is found, the file isn't saved and you'll see an explanation. |
| **Runs entirely on your computer** | Nothing is sent to any server. `privacy.telemetry: off` is hard-coded and cannot be changed, even by an administrator. |
| **Never fabricates citations** | Every link is verified as live and accurate before inclusion. Unverified resources are described in plain English — never written as a fake link. |

---

## FAQ

<details>
<summary>Do I need a Claude.ai account?</summary>

Yes — both Cowork and Claude Code run on Anthropic's Claude AI. Sign up free at [claude.ai](https://claude.ai). A paid plan is not required to get started.

</details>

<details>
<summary>What if I don't have my district's lesson plan template?</summary>

Choose one of three built-in starters during setup: **Weekly block** (90-min periods), **Weekly bell** (5–7 period schedule), or **Daily one-pager**. You can swap in your real template at any time by saying `I have a new district template to upload.`

</details>

<details>
<summary>What if I don't have my state standards?</summary>

The plugin still works — it skips the standard-code step and flags it in the compliance notes at the top of your plan. Add standards any time: `Upload new standards for [subject].`

</details>

<details>
<summary>Can elementary teachers use this?</summary>

Yes. Self-contained classrooms are fully supported. Set up one "subject" (e.g., "3rd Grade") with content areas inside — math, reading, writing, science, social studies. The plugin generates one cohesive plan for your whole day.

</details>

<details>
<summary>Can I use this for co-taught classes?</summary>

Yes. During setup, say the class is co-taught and give your co-teacher's name and role. Differentiation sections will include suggestions for splitting the instructional work between you.

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

Yes. During setup (or via `Update my config`), tell it you have multiple sections. The plugin accounts for them.

</details>

<details>
<summary>Can it post directly to Google Classroom or Canvas?</summary>

Not in this version — LMS integration is on the roadmap. Upload output files manually for now.

</details>

---

## Full teacher guide

For complete documentation including worked examples, framework details, and settings reference, see **[TEACHER_GUIDE.md](TEACHER_GUIDE.md)**.

---

## License

MIT — see [LICENSE](LICENSE).

*Jake's Lesson Plan Magic · v0.2.5 · [jakehallman.com](https://jakehallman.com)*
