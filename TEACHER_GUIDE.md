# Jake's Lesson Plan Magic — Complete Teacher Guide

> **Version 0.2.5 · For K-12 teachers · No tech experience required**

---

## Table of Contents

1. [What Is This?](#1-what-is-this)
2. [What Can It Do?](#2-what-can-it-do)
3. [Two Ways to Use It](#3-two-ways-to-use-it)
4. [What You Need Before You Start](#4-what-you-need-before-you-start)
5. [Installation — Cowork (Recommended)](#5-installation--cowork-recommended)
6. [Installation — Claude Code (Alternative)](#6-installation--claude-code-alternative)
7. [First-Time Setup (Onboarding)](#7-first-time-setup-onboarding)
8. [Making Lesson Plans](#8-making-lesson-plans)
9. [Making Classroom Artifacts](#9-making-classroom-artifacts)
10. [Finding Your Output Files](#10-finding-your-output-files)
11. [Updating Your Settings](#11-updating-your-settings)
12. [Privacy & Student Data](#12-privacy--student-data)
13. [Frequently Asked Questions](#13-frequently-asked-questions)
14. [Quick Reference Card](#14-quick-reference-card)

---

## 1. What Is This?

**Jake's Lesson Plan Magic** is an AI planning assistant you install once and then talk to in plain English. Think of it as a very thorough planning partner who:

- Knows your standards, your schedule, and your district's template
- Writes in your voice — not generic teacher-speak
- Never misses a compliance box
- Hands you a finished Word document, not a wall of text to copy-paste

It does **two main jobs**:

| Job | What you say | What you get |
|---|---|---|
| **Lesson Planner** | "Plan my week for Chemistry" | A filled-in `.docx` lesson plan in your district template |
| **Classroom Artifacts** | "Make me an exit ticket for today" | A ready-to-print `.docx` or `.pptx` file |

Both jobs talk to each other. Once your lesson plan exists, your exit tickets and agenda slides pull from it automatically — you never retype your learning intentions.

---

## 2. What Can It Do?

### Lesson Plans

| Type | When to use it | Example request |
|---|---|---|
| **Weekly plan** | Your bread-and-butter — Monday through Friday for one subject | "Plan my week for Chemistry" |
| **Daily plan** | Re-planning after a disruption, observation day, or sub day | "Make a daily plan for Thursday in Algebra" |
| **Unit plan** | Stepping back to map out 2–6 weeks at once | "Plan the next three weeks of American Literature" |

Each plan includes:
- **Standards** pulled directly from your uploaded state standards (only real codes, never made up)
- **Learning intentions and success criteria** ("I am learning… / I can…")
- **Instructional framework breakdown** in whatever model you use (5E, gradual release, workshop model, direct instruction, SIOP, etc.)
- **Differentiation** for your students — including ELL, IEP/504, gifted, and tiered readiness — written at the accommodation level, never by student name
- **Evidence of learning** so you know what you're looking for
- **Materials list** for anything non-obvious
- **Verified resources** — if a website or video is suggested, the plugin checks that the link actually works before writing it into your plan

### Classroom Artifacts

These are the short, printable things you need every day:

| Artifact | What it is | Output format |
|---|---|---|
| **Agenda slide** | The daily posting at the front of the room | PowerPoint (`.pptx`) |
| **Exit ticket** | 3–5 questions to check understanding at the end of class | Printable Word doc (`.docx`) or Google Forms–ready text |
| **Do-now / bell ringer** | A 5-minute opener students can start independently | Printable Word doc (`.docx`) |
| **Sub plan** | A clear, anyone-can-run-it day plan for when you're out | Word doc (`.docx`) |

---

## 3. Two Ways to Use It

You have two options for running Lesson Plan Magic. **Cowork is the recommended path for most teachers** — it's a purpose-built desktop app with a one-click plugin installer and a cleaner interface. Claude Code is the technical alternative if you're already using it or need deeper control.

| | Cowork | Claude Code |
|---|---|---|
| **Best for** | Most teachers | Teachers comfortable with a developer tool |
| **Installation** | Drag-and-drop the `.plugin` file | File drop + one Terminal command |
| **How you trigger skills** | Type `/lesson-planner` or `/classroom-artifacts` | Just talk — plain English |
| **Connect your calendar** | Yes — connect Google Calendar or Outlook directly as a Connector | Upload an `.ics` file manually |
| **Connect your email** | Yes — connect Gmail or Outlook to pull sub-day context | Not available |
| **Output files** | Same `Documents/Lesson Plan Magic/outputs/` folder | Same folder |
| **Python required** | Yes (one-time setup) | Yes (one-time setup) |

Both produce identical plans and artifacts. The difference is entirely in how you install and interact.

---

## 4. What You Need Before You Start

### Required (either path)
- **Python 3.9 or newer** on your computer
  - On a Mac: open Terminal and type `python3 --version`. If you see `3.9` or higher, you're good.
  - On Windows: open Command Prompt and type `python --version`.
  - If Python isn't installed, download it free at [python.org](https://python.org).
- **The plugin file:** `jakes-lesson-plan-magic.plugin` (included with this package)

### Highly Recommended (collect these before onboarding)
- **Your district lesson plan template** — the `.docx` Word file your school requires you to fill out each week. If you don't have it digitally, ask your instructional coach or department chair.
- **Your state standards** — a PDF, a URL to your state's standards page, or even pasted text. (If you don't have this, the plugin will still work — it just won't be able to cite standard codes.)
- **A folder of past lesson plans** — even 5 or 10 old plans in Word format. The plugin reads these to learn how you write — your density, your warmth, your favorite activities — and applies that voice to everything it generates. The more you give it, the better the match.
- **Your school calendar** — an `.ics` file exported from Google Calendar or Outlook, or a PDF. This lets the plugin skip holidays and testing windows automatically. (Cowork users can connect their calendar directly instead.)

---

## 5. Installation — Cowork (Recommended)

### Step 1 — Download and install Cowork

Cowork is a free desktop app. Download it from [claude.ai/cowork](https://claude.ai/cowork) and install it the same way as any Mac or Windows app.

### Step 2 — Install the plugin

1. Open Cowork.
2. Locate the file `jakes-lesson-plan-magic.plugin` (it came with this package).
3. Drag and drop the `.plugin` file into the Cowork window. A preview card will appear showing the plugin's skills.
4. Click **Accept** (or **Add Plugin**). The plugin is now installed.

That's it for the plugin itself. You'll see two new skills available: **lesson-planner** and **classroom-artifacts**.

### Step 3 — Install Python dependencies

This is a one-time step. It gives the plugin the tools it needs to read and write Word documents, check websites, and scan for student privacy.

**On Mac:**

1. Open the **Terminal** app (search for it in Spotlight with ⌘ Space).
2. Copy and paste this command, then press Enter:

```
pip install python-docx python-pptx pypdf requests beautifulsoup4 rapidfuzz pyyaml
```

3. Wait for it to finish. You'll see text scroll by — that's normal.

**On Windows:**

1. Open **Command Prompt** (search "cmd" in the Start menu).
2. Copy and paste this command, then press Enter:

```
pip install python-docx python-pptx pypdf requests beautifulsoup4 rapidfuzz pyyaml
```

> **Tip:** If you see "pip not found," try `pip3` instead of `pip`.

### Step 4 — Connect your calendar (optional but great)

In Cowork, you can connect your real Google Calendar or Outlook calendar as a **Connector**. Once connected, the plugin automatically knows about holidays, half-days, and testing windows without you uploading anything.

To connect:
1. In Cowork, click **Connectors** in the sidebar.
2. Find **Google Calendar** or **Microsoft Outlook Calendar**.
3. Click **Connect** and sign in with your school account.

You can also connect Gmail or Outlook email if you want the plugin to be able to reference upcoming events you've received.

### Step 5 — Start using it

Type `/lesson-planner` in the Cowork chat to start your first planning session. If it's your first time, the plugin will walk you through a 10–20 minute setup conversation. See [Section 7 — First-Time Setup](#7-first-time-setup-onboarding) for what to expect.

**Tip:** In Cowork, type `/` at any time to see a list of all your available skills.

---

## 6. Installation — Claude Code (Alternative)

Use this path if you're already running Claude Code, or if your IT department has set it up for you.

### Step 1 — Install the plugin

1. Locate the file `jakes-lesson-plan-magic.plugin`.
2. Open Claude Code.
3. Go to **Settings → Plugins** (or use your plugin manager).
4. Click **Install from file** and select `jakes-lesson-plan-magic.plugin`.
5. Enable the plugin from the plugin list.

### Step 2 — Install Python dependencies

**On Mac:**

```
pip install python-docx python-pptx pypdf requests beautifulsoup4 rapidfuzz pyyaml
```

**On Windows:**

```
pip install python-docx python-pptx pypdf requests beautifulsoup4 rapidfuzz pyyaml
```

> **Tip:** If you see "pip not found," try `pip3` instead of `pip`.

### Step 3 — Start using it

Just talk to Claude Code in plain English — "Plan my week for Chemistry" — and the plugin kicks in automatically. You do not need to type a slash command in Claude Code; it recognizes planning requests and routes them to the right skill on its own.

---

## 7. First-Time Setup (Onboarding)

The first time you trigger a planning request — either by typing `/lesson-planner` in Cowork or saying "plan my week" in Claude Code — the plugin starts a 10–20 minute setup conversation. This is a **conversation**, not a form. You can answer in plain English, upload files mid-chat, or skip any optional step.

Progress is saved automatically after each step, so if you get interrupted, you can pick up where you left off next time.

---

### Step 1 — Your basics

> "I'll help you set up Lesson Plan Magic. Takes 10-20 minutes depending on how much you upload. You can drop files at any point or answer in chat. Let's start: your name, state, and school?"

**You answer:** Something like "Jane Smith, Ohio, Central High School."

---

### Step 2 — Your experience level

It will ask which fits best:
- New teacher (0–3 years)
- Mid-career (3–10 years)
- Veteran (10+ years)
- Veteran, but new to this subject

**Why does this matter?** It affects how much pedagogy jargon appears in your plans. A first-year teacher gets frameworks explained in plain language. A 20-year veteran gets terse, dense plans that don't waste their time on things they already know. Once your past plans are uploaded, the plugin adjusts further based on how you actually write — so this initial setting is just a starting point.

---

### Step 3 — Your subjects

> "How many preps do you have, and what are they?"

**Examples of how to answer:**
- "I teach Chemistry I and AP Chemistry."
- "I'm 4th grade, self-contained — math, reading, writing, science, social studies."
- "Just Algebra I, but I have three sections of it."
- "I co-teach Algebra I with a special-ed teacher."

Elementary teachers: you set up **one subject** with multiple content areas inside it. Secondary teachers: each prep is a separate subject.

---

### Step 4 — Per-subject setup

For each subject, it will ask several things in one go (not nine separate questions):

**Standards** — How do you want to supply them?
- Upload a PDF (drag and drop a state standards document)
- Paste a URL to your state's standards page
- Paste text
- Skip for now (you'll get a compliance note at plan time, but it still works)

**Template** — Your district lesson plan document:
- Upload your `.docx` template
- Or choose a built-in starter: weekly block (90-min), weekly bell schedule, or daily one-pager

**Schedule** — What does a typical week look like?
- 45-min periods, 5 days a week
- 90-min block schedule
- A/B rotation (alternating days)
- Elementary all-day

**Pedagogy framework** — Does your school or district require a specific instructional model?

| Framework | What it is |
|---|---|
| 5E | Engage, Explore, Explain, Elaborate, Evaluate |
| Gradual release | I Do / We Do / You Do |
| Workshop model | Mini-lesson + workshop time + share |
| SWIRL | Speaking, Writing, Interacting, Reading, Listening tagging |
| SIOP | Sheltered Instruction Observation Protocol |
| UDL | Universal Design for Learning |
| Direct instruction | Explicit, scripted, teacher-led |
| Project-based | Inquiry-driven / PBL |
| Marzano / Hattie | Research-based high-yield strategies |
| None | No framework required |
| Custom | Upload your district's own framework document |

**Differentiation** — Which populations are in your classroom?
- Tiered ability levels (novice, on-level, advanced)
- English Language Learners (ELL)
- Students with IEPs
- Students with 504 plans
- Gifted students

---

### Step 5 — Past plans (optional, but worth it)

> "Drop a folder of past lesson plans if you have any. I'll extract your layout, voice, favorite activities, and pacing."

This is the step that makes the plugin feel like you wrote it yourself. It reads your old plans and builds a **voice profile** — how dense your plans are, whether you write full paragraphs or terse bullets, how warm your language is, your signature activities and transitions.

**You don't have to do this** — the plugin works without it. But teachers who upload even 5–10 past plans consistently say the output sounds like them.

What to upload: a folder of Word documents (`.docx`). Old plans, observation-day plans, sub plans — all of it works.

---

### Step 6 — School calendar (optional)

If you **didn't** connect your calendar as a Cowork Connector in Step 4 of installation, you can upload your school-year calendar here: an `.ics` file from Google Calendar or Outlook, or a PDF from your district's website.

With a calendar loaded, the plugin automatically skips holidays, avoids planning on testing days, and re-sequences around half-days. Without it, mention special days when you ask for a plan ("skip Thursday — it's a half day").

---

### Step 7 — All set

At the end, the plugin writes a file called `config.yaml` to your Documents folder and gives you a plain-English summary:

> "All set. I'll plan: Chemistry, AP Chemistry. Standards: Ohio NGSS + College Board AP. Template: your district Word doc. Framework: 5E + gradual release. Voice: learned from 18 past plans. Try 'plan Chemistry for next week.'"

**You will never need to do onboarding again.** Every future request goes straight to planning.

---

## 8. Making Lesson Plans

### How to trigger it

**In Cowork:** Type `/lesson-planner` to open the skill, then describe what you need. Example:

```
/lesson-planner Plan my week for Chemistry.
```

Or just type `/lesson-planner` alone and it will prompt you.

**In Claude Code:** Just talk naturally — the plugin picks up planning requests automatically:

```
Plan my week for Chemistry.
```

---

### Example requests (use these exactly or adapt freely)

```
Plan my week for Chemistry.
```
```
Plan next week for AP Chemistry.
```
```
Make a lesson plan for Monday in Geometry.
```
```
I need a daily plan for Friday — I have an administrator observation.
```
```
Plan the next unit of American Literature. Three weeks, ending with a Socratic seminar.
```
```
Plan the next two weeks for 3rd grade math.
```
```
What should I teach next week? We just finished the Civil War unit.
```

---

### What happens after you ask

1. **It may ask 2–3 clarifying questions** in a single message — things like "Last week you ended on photosynthesis. Ready for cellular respiration, or do you want a review day first?" or "Your calendar shows a half-day Thursday — should I shorten that lesson or re-sequence?" If nothing needs clarifying, it skips this step.

2. **It drafts the plan** — each day is drafted by a separate AI model running at the same time, so a full weekly plan doesn't take five times as long as a daily plan.

3. **It checks the plan** against a compliance checklist (standards cited, success criteria measurable, differentiation included, etc.) and notes any warnings at the top of the document.

4. **It fills your template** — the plan goes into your uploaded district Word document, in the right cells, with your voice applied.

5. **It delivers the file** to `Documents/Lesson Plan Magic/outputs/` and tells you the filename.

6. **It may ask** (once, briefly) if you want agenda slides, exit tickets, do-nows, or a sub plan for the week.

---

### Worked examples

**Example 1 — Basic weekly plan**

> You: `Plan my week for Chemistry.`

> Plugin: "Quick check — last week ended with molar mass calculations. Ready to move into stoichiometry, or do you want a one-day spiral review first? Also, any assemblies or testing this week?"

> You: "Spiral review Monday, then stoichiometry Tuesday through Friday."

> Plugin: *[drafts plan, checks compliance, fills template]*
> "Done. Your plan is at: Documents/Lesson Plan Magic/outputs/2026-04-21_to_2026-04-25_chem.docx — Want agenda slides, exit tickets, or a sub plan for any of these days?"

---

**Example 2 — Observation day**

> You: `I need a really polished daily plan for Thursday in AP Chemistry — my principal is observing.`

> Plugin: "Got it. Any specific standard you want to feature? Or I can pull from where you left off in equilibrium."

> You: "Equilibrium — Le Chatelier's Principle."

> Plugin: *[drafts plan with full voice polish]*
> "Done. Observation plan at: Documents/Lesson Plan Magic/outputs/2026-04-24_ap-chem.docx"

---

**Example 3 — Unit plan**

> You: `Plan the next three weeks of American Lit. We just finished The Great Gatsby. I want to move into Harlem Renaissance poetry, ending with a written analysis.`

> Plugin: "Got it — 3 weeks, Harlem Renaissance poetry, culminating in a written analysis. A few questions: Do you want a formative in week 2, or just the summative at the end? Primary texts only, or paired contemporary work?"

> You: "Formative in week 2 — a quick poem annotation. Primary texts only."

> Plugin: *[generates unit arc, then three weekly plans]*
> "Done. Unit plan at: Documents/Lesson Plan Magic/outputs/unit_2026-04-21_to_2026-05-08_amer-lit.docx"

---

**Example 4 — Elementary self-contained**

> You: `Plan my week. We're starting multiplication with 2-digit numbers in math, and in reading we're on chapter 4 of Charlotte's Web.`

> Plugin: *[plans all content areas — math, reading/ELA, science, writing, social studies — for the full week]*
> "Done. Your weekly plan is at: Documents/Lesson Plan Magic/outputs/2026-04-21_to_2026-04-25_grade-3-self-contained.docx"

---

**Example 5 — Re-planning after a disruption**

> You: `We had a fire drill Thursday and lost 30 minutes. I need to re-plan Friday's Chemistry lesson — we didn't finish the lab intro.`

> Plugin: "Got it — picking up from the pre-lab safety steps. Friday will open with a 15-minute recap, then move into the procedure. Want me to push Monday's standard back, or can we absorb this in the lab itself?"

> You: "Absorb it in the lab."

> Plugin: *[generates revised Friday daily plan]*
> "Updated daily plan at: Documents/Lesson Plan Magic/outputs/2026-04-25_chem.docx"

---

### What's in a typical weekly plan

Here's a realistic example of one day block inside the finished Word document:

```
MONDAY — April 21, 2026

Standards: HS-PS1-7 (Use mathematical representations to support 
           the claim that atoms are conserved during a chemical reaction.)

Learning intention: I am learning to balance chemical equations using 
                    conservation of mass.
Success criteria:   I can write balanced equations for simple reactions 
                    without a calculator.

Opening (10 min)
  Do-now on whiteboard: "What stays the same when you burn wood?"
  Review previous exit ticket data — address top misconception.

I Do / Mini-Lesson (20 min)
  Model balancing H₂ + O₂ → H₂O. Think aloud: coefficient vs. subscript.
  Common mistake: changing subscripts instead of coefficients — address directly.

We Do (25 min)
  Guided practice: pairs work through 3 progressively harder equations 
  on whiteboards. Circulate; listen for subscript errors.

You Do (25 min)
  Independent: 5 equations from worksheet section A.
  Students with IEP-specified accommodations: pre-filled reactant side; 
  focus on balancing products only.
  For students ready to extend: section B (polyatomic ions).

Closing (10 min)
  Exit ticket (see 2026-04-21_chem_exit-ticket.docx).
  Preview: Tuesday lab — what equipment will we use?

Materials: Whiteboard markers, equation practice worksheet (A + B), 
           exit ticket half-sheets

Evidence of learning: 
  Circulate during We Do and listen for coefficient vs. subscript confusion. 
  Exit ticket results reviewed before Tuesday.
```

---

### Pedagogy framework tags

If you use SWIRL, the plan automatically tags each component:

```
Opening [L — Listening, S — Speaking]
Mini-lesson [L — Listening]
We Do [S — Speaking, I — Interacting]
You Do [W — Writing]
Closing [W — Writing, S — Speaking]
```

If you use 5E, the plan is structured as Engage / Explore / Explain / Elaborate / Evaluate instead of the gradual-release format shown above.

---

## 9. Making Classroom Artifacts

All artifacts pull their learning intention and agenda directly from your existing plan — you never have to retype anything.

### How to trigger it

**In Cowork:** Type `/classroom-artifacts` and describe what you need:

```
/classroom-artifacts Exit ticket for today's Chemistry.
```

**In Claude Code:** Just ask naturally:

```
Exit ticket for today's Chemistry.
```

---

### Agenda slides

**Example requests:**

```
/classroom-artifacts Make me an agenda slide for today.
```
```
Agenda slides for all my subjects today.
```
```
Agenda slide for Thursday's AP Chemistry.
```

**What you get:** A `.pptx` PowerPoint file with one slide per subject. Each slide includes:
- Learning intention ("I am learning…")
- Success criteria ("I can…")
- Today's agenda (3–6 bullets, in order)
- Homework / materials for tomorrow
- Class name and date

**Example slide content:**

```
Chemistry I — Monday, April 21

I am learning:
   To balance chemical equations using conservation of mass.

I can:
   Write balanced equations for simple reactions.

Today's agenda:
   1. Do-now (10 min)
   2. Mini-lesson: balancing equations (20 min)
   3. Whiteboard practice with partners (25 min)
   4. Independent practice (25 min)
   5. Exit ticket (10 min)

For tomorrow: Bring safety goggles — lab day.
```

**Output file:** `2026-04-21_chem_agenda.pptx`

---

### Exit tickets

**Example requests:**

```
Exit ticket for today's Chemistry.
```
```
Exit ticket for Monday's Biology.
```
```
Exit ticket for Thursday — Google Forms format.
```

**What you get:** A Word document formatted as a half-sheet (print one page, cut in half for two tickets). Or, if you ask for Google Forms format, a plain text file you can copy-paste directly into a Google Form.

**Example exit ticket content:**

```
Name: _______________     Period: ___    Date: April 21

Chemistry I — Exit Ticket

1. Balance this equation: H₂ + O₂ → H₂O

2. A student changes a subscript instead of a coefficient to balance 
   an equation. What's wrong with that?

3. Rate your confidence with balancing equations today: 
   1 (totally lost) — 2 — 3 — 4 — 5 (could teach it)

★ Extension (if finished): Balance: CH₄ + O₂ → CO₂ + H₂O
```

**Output file:** `2026-04-21_chem_exit-ticket.docx`

---

### Do-nows / bell ringers

**Example requests:**

```
Do-now for tomorrow's Chemistry.
```
```
Bell ringer for Monday's Algebra.
```
```
Give me a do-now that spirals back to last week's vocabulary.
```

**What you get:** A one-page Word document with a single prompt, self-explanatory instructions, and enough context for a student to start independently.

**Example do-now content:**

```
Do-Now — Chemistry I
Tuesday, April 22

Look at these two "balanced" equations. One is correct. One is wrong.
Figure out which is which, and explain the mistake.

   Equation A: 2 H₂ + O₂ → 2 H₂O
   Equation B: H₂ + O₂ → H₂O₂

Write your answer in your notebook before class begins.
```

**Output file:** `2026-04-22_chem_do-now.docx`

---

### Sub plans

**Example requests:**

```
Sub plan for tomorrow — I'm out sick.
```
```
Quick sub plan for Friday, just Chemistry 3rd period.
```
```
I need a sub plan for Thursday. Make it something students can do independently.
```

**What you get:** A one-page Word document that any adult can use to run your class.

**Example sub plan content:**

```
SUBSTITUTE TEACHER PLAN
Teacher: Ms. Smith          Subject: Chemistry I
Date: April 24, 2026        Period: 3 (10:15–11:45 AM)

ATTENDANCE
Use the seating chart in the top drawer of my desk. Mark anyone missing 
on the yellow slip and send it to the office by 10:30.

TODAY'S ACTIVITY — "Balancing Equations Practice" (approx. 50 min)
Students already know this material — this is independent practice, 
not new content.

1. Students pick up the worksheet from the front tray (labeled "Sub Day").
2. They work independently on equations 1–15.
3. Answer key is in the green folder on my desk. 
   Go over answers as a class in the last 10 minutes.

MATERIALS
• Worksheets: front tray on my desk (already printed, 35 copies)
• Answer key: green folder on my desk

IF PLAN A FAILS (students say they've done this worksheet)
Have students watch the video on the sticky note inside the green folder 
and answer the reflection questions on the back of the worksheet.

COLLECT: All completed worksheets. Leave in a stack on my desk.

EMERGENCY CONTACTS
Front office: ext. 100
Nearest colleague: Mr. Johnson, Room 214
```

**Output file:** `2026-04-24_chem_sub-plan.docx`

---

## 10. Finding Your Output Files

All files go into one folder on your computer:

**Mac / Linux:**
```
Documents/Lesson Plan Magic/outputs/
```

**Windows:**
```
Documents\Lesson Plan Magic\outputs\
```

Files are named by date and subject:

```
2026-04-21_to_2026-04-25_chem.docx          ← weekly lesson plan, Chemistry
2026-04-21_chem_agenda.pptx                  ← agenda slide
2026-04-21_chem_exit-ticket.docx             ← exit ticket
2026-04-22_chem_do-now.docx                  ← do-now
2026-04-24_chem_sub-plan.docx                ← sub plan
2026-04-21_to_2026-04-28_amer-lit.docx       ← weekly plan, American Literature
```

**Opening files:** Double-click any `.docx` to open in Word or Google Docs. Double-click any `.pptx` to open in PowerPoint or Google Slides.

**Posting to Google Classroom / Canvas:** Open the file, make any personal edits, and upload manually. (Direct LMS posting is planned for a future version.)

**Old files:** The plugin never auto-deletes anything. Clean out the `outputs/` folder whenever you like — deleting old files is safe.

---

## 11. Updating Your Settings

Your settings live in a file called `config.yaml` inside `Documents/Lesson Plan Magic/`. You never need to touch this file directly.

### Ways to update

**By talking to the plugin:**

```
Update my config.
```
```
Add a new subject — I'm picking up a section of Geometry next semester.
```
```
I switched to a new district template. How do I upload it?
```
```
Change my voice match level to strict — I have a big observation coming up.
```

**Automatically:** If you mention a subject the plugin doesn't recognize, it will ask if you want to add it and walk you through setup for that subject.

**Manually:** Open `config.yaml` in any text editor and change things directly. The plugin validates the file on every run.

---

### Common settings

| Setting | What it controls | Options |
|---|---|---|
| `research_depth` | Whether to include verified web links | `off` · `generic-queries` · `verified` (default) |
| `compliance_mode` | How strict the pre-delivery check is | `strict` · `soft-warn` (default) · `off` |
| `voice_match_level` | How closely the output matches your writing style | `generic` · `calibrated` (default) · `strict` |
| `bonus_artifacts_prompt` | Whether to offer exit tickets / agenda slides after each plan | `true` (default) · `false` |

**Research depth:**
- `off` — No external links in your plans
- `generic-queries` — Suggests things like "find a 3-minute video on X" without a link (good if your district blocks web searching)
- `verified` — Every link is checked to be live and accurate before it appears in your plan (default, recommended)

**Voice match level:**
- `generic` — Standard educator voice; doesn't try to sound like you
- `calibrated` — Uses your voice profile from past plans (default when you've uploaded past plans)
- `strict` — Highest-quality voice matching; best for observation days; takes slightly longer

---

## 12. Privacy & Student Data

### What the plugin will never do

- **Never write a student's name.** If you mention "Jamie needs extended time," the plan says "students with extended-time accommodations" — not Jamie's name.
- **Never invent a standard code.** If it can't find a real code, it says so.
- **Never include a broken link.** Unverified resources are described in plain English, not written as links.
- **Never send your data anywhere.** The plugin works entirely on your computer. No telemetry, no phone-home. This is a hard setting that cannot be changed.

### Built-in privacy scan

Every file goes through an automatic scan before it's saved. The scanner catches:
- Student names
- Social Security numbers
- Phone numbers and email addresses
- Student ID numbers
- Date-of-birth formats
- Home address patterns
- IEP/504 accommodation language tied to specific students
- Medical and discipline note patterns

If the scan detects something, the file is **not written** and you'll see a message explaining why. This means you can paste messy notes without worrying about accidentally writing protected information into a plan.

### Historical figures are fine

The scanner won't flag Abraham Lincoln, Rosa Parks, or Shakespeare. If it trips on a name that's clearly not a student — your co-teacher, a historical figure — tell the plugin:

```
Add "Ms. Rodriguez" to my approved names list.
```

### FERPA note

This plugin is designed to help you write differentiation plans that address student needs without naming individuals. It is not a substitute for your district's legal guidance or your own professional judgment.

---

## 13. Frequently Asked Questions

**Q: Do I have to type the slash command in Cowork, or can I just talk normally?**

You can do either. `/lesson-planner Plan my week for Chemistry` and just `Plan my week for Chemistry` both work in Cowork. The slash command is helpful because it gives Cowork a precise hook to activate the right skill immediately; plain English works too, especially mid-conversation.

---

**Q: What's the difference between Cowork and Claude Code — really?**

They're both AI assistants that run this plugin. Cowork is a cleaner, more approachable desktop app for knowledge workers — it has a plugin installer built right in, a `/skills` menu, and can connect directly to your calendar and email. Claude Code is a more technical tool aimed at developers. If you're not sure which to use, choose Cowork.

---

**Q: Do I need a Claude.ai account?**

Yes — both Cowork and Claude Code run on Anthropic's Claude AI. You'll need a Claude.ai account (free or paid). Sign up at [claude.ai](https://claude.ai).

---

**Q: What if I don't have my district's lesson plan template?**

Choose one of three built-in starters during onboarding:
- **Weekly block** — designed for 90-minute periods, 5 days, table format
- **Weekly bell** — designed for 5-7 period bell schedules
- **Daily one-pager** — clean single-day format

---

**Q: What if I don't have my state standards?**

The plugin still works — it skips the standards-citation step and flags that in the compliance notes. Add standards later by saying "update my config" and uploading a PDF.

---

**Q: Can I use this for co-taught classes?**

Yes. During onboarding, say the class is co-taught and give your co-teacher's name and role (special education, ELL support, or content specialist). The differentiation sections will automatically include suggestions for splitting the instructional work between you.

---

**Q: Can elementary teachers use this?**

Yes. Self-contained classrooms are fully supported. You set up one "subject" (e.g., "3rd Grade") with content areas inside (math, reading, writing, science, social studies). The plugin generates one cohesive plan for your whole day.

---

**Q: The plan doesn't sound like me. What do I do?**

First, check that you uploaded past plans during onboarding — voice matching gets dramatically better with even 5–10 old Word documents. If you have and it still sounds off:

```
The output doesn't sound like me — can you adjust the voice?
```

Or: `Set my voice match level to strict.`

---

**Q: My school uses a framework that isn't in the list.**

During onboarding (or via "update my config"), upload your district's framework document — a Word doc or plain text file. The plugin reads it and uses it alongside or instead of the built-in frameworks.

---

**Q: Can I get a PDF instead of a Word document?**

Not yet — PDF export is on the roadmap. For now, open the `.docx` in Word and use File → Save As → PDF, or open it in Google Docs and use File → Download → PDF.

---

**Q: Can it post directly to Google Classroom or Canvas?**

Not in this version. LMS integration is planned. Upload files manually for now.

---

**Q: I teach three sections of the same class. Will the plan cover all of them?**

Yes. Set `periods_per_day: 3` for that subject during onboarding (or say "update my config"). The plugin accounts for multiple sections.

---

**Q: I got interrupted during onboarding. How do I resume?**

Go back to Cowork or Claude Code and say: "Resume my setup" or "I got interrupted during onboarding — where did we leave off?" Progress is saved automatically.

---

**Q: Is it safe to delete old files in the outputs folder?**

Yes. Delete anything you don't need. The plugin doesn't re-read old plans unless you explicitly ask it to use them for voice learning (past-plans ingestion).

---

## 14. Quick Reference Card

---

### Triggering skills

| App | Lesson planner | Classroom artifacts |
|---|---|---|
| **Cowork** | `/lesson-planner [request]` | `/classroom-artifacts [request]` |
| **Claude Code** | Just talk — "Plan my week for Chemistry" | Just talk — "Exit ticket for today" |

In Cowork, type `/` to see all available skills at any time.

---

### Lesson plans

| What you want | What to say |
|---|---|
| Weekly plan | `Plan my week for [subject].` |
| Weekly plan, specific dates | `Plan April 28 through May 2 for [subject].` |
| Daily plan | `Daily plan for [day] in [subject].` |
| Unit plan | `Plan the next [N] weeks of [subject].` |
| Re-plan after disruption | `We lost time on [day]. Re-plan [day/rest of week].` |
| Observation day polish | `Polish my plan for [day] — I have an observation.` |
| First run / setup | `Set up Lesson Plan Magic.` or just `Plan my week.` |

### Classroom artifacts

| What you want | What to say |
|---|---|
| Agenda slide (today) | `Agenda slide for today.` |
| Agenda slide (all subjects) | `Agenda slides for all my subjects today.` |
| Agenda slide (specific day) | `Agenda slide for [day]'s [subject].` |
| Exit ticket | `Exit ticket for [day]'s [subject].` |
| Exit ticket (Google Forms) | `Exit ticket for [day] — Google Forms format.` |
| Do-now | `Do-now for [day]'s [subject].` |
| Sub plan | `Sub plan for [day] — I'm out.` |
| Sub plan (one period) | `Sub plan for [day], [subject] [period].` |

### Settings and updates

| What you want | What to say |
|---|---|
| Update any setting | `Update my config.` |
| Add a subject | `Add a new subject — [subject name].` |
| Upload new template | `I have a new district template to upload.` |
| Upload new standards | `Upload new standards for [subject].` |
| Approve a name | `Add "[name]" to my approved names list.` |
| Connect calendar (Cowork) | Use the Connectors panel in the Cowork sidebar |

### Output file location

**Mac:** `Documents/Lesson Plan Magic/outputs/`  
**Windows:** `Documents\Lesson Plan Magic\outputs\`

File naming: `YYYY-MM-DD_subjectid_type.ext`

| File | Name example |
|---|---|
| Weekly plan | `2026-04-21_to_2026-04-25_chem.docx` |
| Agenda slide | `2026-04-21_chem_agenda.pptx` |
| Exit ticket | `2026-04-21_chem_exit-ticket.docx` |
| Do-now | `2026-04-21_chem_do-now.docx` |
| Sub plan | `2026-04-21_chem_sub-plan.docx` |

---

*Jake's Lesson Plan Magic · v0.2.5 · MIT License · jakehallman.com*
