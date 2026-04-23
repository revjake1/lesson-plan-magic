# Config Schema

The teacher's config lives at `~/Documents/Lesson Plan Magic/config.yaml` (default; override-able on first run). This doc is the source of truth for what the system knows about each teacher.

## Top-level structure

```yaml
version: "0.3.0"            # schema version — used for future migrations
teacher: {...}              # identity + experience level
subjects: [...]             # one or more subject profiles
defaults: {...}             # output prefs, research depth, compliance mode
privacy: {...}              # FERPA invariants (not user-overridable)
```

## `teacher` block

```yaml
teacher:
  name: "Jane Smith"                    # required; display only, never written into plans
  experience_level: veteran             # required; one of: new | mid-career | veteran | new-to-subject
  district: "Anytown USD"               # optional
  state: "OH"                           # required; US 2-letter state code; used to infer state standards framework if unspecified
  school: "Central High School"         # optional
  subjects_taught_count: 3              # derived from len(subjects); don't set manually
```

`experience_level` gates how much pedagogy jargon the runtime uses. These are defaults; the teacher's voice profile (once extracted from past plans) overrides them.

- `new` — 0-3 years; favor plain language, explain frameworks in line
- `mid-career` — 3-10 years; normal pedagogy vocab
- `veteran` — 10+ years; terser explanations by default, but jargon density is driven by the teacher's voice profile, not years alone — a 25-year math teacher who's never worked in a SIOP building should still get SIOP components explained in line on the first few plans
- `new-to-subject` — experienced teacher, new content; normal vocab but offer content-area scaffolding

## `subjects` array

Each subject is a separate profile. Most teachers have 1-4 subjects. Elementary self-contained teachers have ONE subject with multiple `content_areas` inside (see below).

### Standard subject (secondary / departmentalized)

```yaml
subjects:
  - id: chem                            # required; kebab-case; used in filenames
    name: "Chemistry I"                 # required; display name
    subject_type: departmentalized      # required; one of: departmentalized | elementary-self-contained | co-taught

    standards:
      - path: "standards/oh-nglss-chem.pdf"      # relative to config dir; OR
      # - url: "https://..."                     # the plugin fetches + caches; OR
      # - inline: "HS-PS1-1 Use the periodic..." # pasted text

    template:
      path: "templates/weekly-chem.docx"         # relative to config dir
      mapping_verified: true                     # has the teacher confirmed field mapping? first-run sets false; confirmed on first successful fill

    schedule:
      type: block                                # block | bell | elementary | ab-rotation | custom
      period_length_minutes: 90
      days: [M, T, W, R, F]                      # school days this subject meets
      periods_per_day: 1
      # periods_per_day: NUMBER OF SECTIONS the teacher teaches of THIS
      # subject on a typical day. Most teachers with one section of a
      # subject leave this at 1. A math teacher with three sections of
      # Algebra I in a bell schedule sets periods_per_day: 3 for that
      # subject. Unrelated to daily_blocks (elementary) or any notion of
      # "this subject meets twice per day" — it's section count.
      rotation: null                             # "A/B" for A/B schools; null for non-rotating

    frameworks: ["5e", "udl"]                    # 0-N framework IDs; see framework-primers/
    custom_framework_path: null                  # optional path to a district framework doc (relative to config dir)
    # When set, the pipeline reads the file at plan time and passes the
    # extracted name + components into the per-day prompt alongside any
    # standard framework IDs listed above. Accepted formats: .md or .txt.
    # The framework ID used in prompts is "custom:<filename stem>"
    # (e.g., custom:bcss-framework). Not cached across plans — re-read on
    # each invocation so districts can edit in place.

    differentiation:
      tiers: [novice, on-level, advanced]        # ability tiers to address; [] to disable tiered differentiation
      populations: [ELL, SPED_IEP]               # array of: ELL | SPED_IEP | SPED_504 | GIFTED
      # Each configured population triggers its differentiation playbook at plan time.

    past_plans_dir: "past-plans/chem/"           # where the teacher's past plans for this subject live
    voice_profile: "past-plans/chem/voice-profile.md"  # auto-derived from past_plans_dir by ingest_past_plans.py; null on cold start
    # voice_profile IS the output of ingesting past_plans_dir. If you
    # change past_plans_dir, re-run ingest to refresh voice_profile — the
    # onboarding flow does this automatically on first run and whenever
    # the teacher drops new files into past_plans_dir.
    pacing:
      scope_and_sequence: "scope-and-sequence/chem-2025-26.md"  # optional; scope-and-sequence doc
      last_planned_week_end: "2026-04-18"        # updated automatically after each plan generation
      current_unit: "Thermochemistry"            # updated from context or asked; informs next-week planning
```

### Elementary self-contained subject

Same teacher, same kids, same room, multiple content areas. ONE subject profile with a `content_areas` array inside.

```yaml
subjects:
  - id: grade-3-self-contained
    name: "3rd Grade"
    subject_type: elementary-self-contained

    schedule:
      type: elementary
      days: [M, T, W, R, F]
      # Total daily minutes are computed from daily_blocks; don't set them
      # manually — it only drifts when a teacher edits the block list and
      # forgets to update the total. The orchestrator sums block lengths
      # and surfaces the total to prompts as `schedule.computed_minutes`.
      daily_blocks:
        - { start: "08:30", end: "09:30", content_area: math }
        - { start: "09:30", end: "10:30", content_area: ela }
        - { start: "10:30", end: "10:45", content_area: null }        # recess, break, transition
        - { start: "10:45", end: "11:30", content_area: science }
        - { start: "12:30", end: "13:15", content_area: social-studies }
        - { start: "13:15", end: "14:00", content_area: writing }
        - { start: "14:00", end: "14:45", content_area: specials }    # art / music / PE; often not planned by classroom teacher

    content_areas:
      - id: math
        name: "3rd Grade Math"
        standards: [{ path: "standards/ca-ccss-math-3.pdf" }]
        template: { path: "templates/weekly-math.docx" }
        pacing:
          scope_and_sequence: "scope-and-sequence/math.md"
          current_unit: "Multiplication and Division"
      - id: ela
        name: "3rd Grade ELA"
        standards: [{ path: "standards/ca-ccss-ela-3.pdf" }]
        template: { path: "templates/weekly-ela.docx" }
      - id: science
        name: "3rd Grade Science"
        standards: [{ path: "standards/ca-ngss-3.pdf" }]
        template: { path: "templates/weekly-science.docx" }
      # ... etc

    # Shared across ALL content areas (because same teacher, same kids):
    frameworks: ["gradual-release"]
    differentiation:
      tiers: [on-level, extension]
      populations: [ELL, SPED_IEP]
    voice_profile: "past-plans/voice-profile.md"   # shared voice
    past_plans_dir: "past-plans/"                  # shared past plans folder, organized by content area inside
```

### Co-taught subject

```yaml
subjects:
  - id: alg1-cotaught
    name: "Algebra I (co-taught)"
    subject_type: co-taught
    co_teacher_name: "Ms. Rodriguez"              # display only, not written in plans
    co_teacher_role: "special-education"          # one of: special-education | ELL-support | content-specialist
    # ... rest same as standard subject
    # Differentiation sections will automatically weave in co-teacher move suggestions.
```

## `defaults` block

```yaml
defaults:
  output_formats: [docx]                          # v0.3.0 ships docx only; pdf and google-doc are planned

  research_depth: verified                        # off | generic-queries | verified
    # off: no external resources suggested
    # generic-queries: "find a 3-5 min video on X" — no link, teacher searches
    # verified: live web search + URL verification before citing (DEFAULT)

  compliance_mode: soft-warn                      # strict | soft-warn | off
    # strict: block delivery if required elements missing
    # soft-warn: deliver with warnings at top (DEFAULT)
    # off: no compliance checking

  voice_match_level: calibrated                   # generic | calibrated | strict
    # generic: teacher voice unused; standard educator tone
    # calibrated: apply extracted voice-profile.md (DEFAULT if profile exists)
    # strict: apply voice-profile.md AND reject drafts that diverge significantly

  bonus_artifacts_prompt: true                    # after weekly plan, ask "want agenda slides / exit tickets / etc.?"
  calendar_path: "calendar/2025-26.ics"           # optional; .ics or text-based .pdf
```

## `approved_names` block (top-level, optional)

```yaml
approved_names:
  - "Rosa Parks"
  - "Ms. Rodriguez"       # co-teacher; auto-added when co_teacher_name is set
  - "Jane Smith"          # teacher; auto-added from teacher.name — you rarely set this by hand
```

`approved_names` is a top-level list of "Firstname Lastname" pairs that
the PII scanner will NOT flag as bare names. The plugin auto-allowlists
two categories for you:

- The teacher's own name (`teacher.name`) — not student PII.
- Co-teacher names (`subjects[].co_teacher_name`) — display-only, per
  the `co-taught` subject schema above.

Add entries here for historical / public figures the plan scanner
keeps tripping on (`DEFAULT_ALLOWED_NAMES` in `fill_template.py`
already covers the common K-12 ones: Rosa Parks, Lincoln, Shakespeare,
etc.). You can also pass one-off names on the CLI via
`--allow-names "Name One,Name Two"` without editing config.

Student names go in *neither* place — they never appear in plans at
all. See hard rule #1.

## `privacy` block

```yaml
privacy:
  student_data: never                             # HARD INVARIANT — not user-overridable, value is always "never"
  pii_scan_before_write: true                     # every output scanned for names/SSNs/etc. before write (HARD INVARIANT)
  retention_days: 365                             # optional advisory retention target; not auto-enforced by the plugin
  telemetry: off                                  # HARD INVARIANT — plugin does not phone home
  # Output retention: not auto-pruned. Older plans live under
  # ~/Documents/Lesson Plan Magic/outputs/ until the teacher deletes
  # them. If you want automated pruning, set up a scheduled task via the
  # `schedule` skill that runs `find outputs/ -mtime +365 -delete`.
  # (The plugin deliberately does not ship its own prune cron — silent
  # deletion of instructional records is a compliance trap.)
```

## ID conventions

- Subject IDs: kebab-case, short, used in filenames. E.g., `chem`, `ap-chem`, `grade-3-self-contained`.
- Content area IDs: kebab-case, standardized where possible: `math`, `ela`, `science`, `social-studies`, `writing`, `specials`.
- Framework IDs: kebab-case, from the fixed list below.

## Framework IDs (v0.3.0 supported)

- `swirl` — Speaking, Writing, Interacting, Reading, Listening tagging
- `udl` — Universal Design for Learning
- `5e` — Engage, Explore, Explain, Elaborate, Evaluate
- `siop` — Sheltered Instruction Observation Protocol
- `gradual-release` — I Do / We Do / You Do
- `marzano` — Marzano's High-Yield Strategies
- `hattie` — Hattie's top-effect-size influences
- `workshop-model` — mini-lesson + workshop time + share
- `direct-instruction` — explicit, scripted, teacher-led
- `project-based` — PBL / inquiry-driven

Multiple frameworks can be listed. A common combination is `["gradual-release", "swirl"]`.

For district-specific frameworks not in the list: use `custom_framework_path` in the subject block and upload the district's framework doc.

## Validation rules (implement in scripts/)

- `teacher.state` is a valid US 2-letter code
- Every `subjects[].id` is unique
- Every `subjects[].content_areas[].id` is unique within the subject
- Every path referenced resolves to an existing file
- `frameworks[]` entries are in the known list OR `custom_framework_path` is set
- `privacy.student_data` is always `never` (reject any other value on load)
- `privacy.telemetry` is always `off`
