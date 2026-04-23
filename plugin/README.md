# Jake's Lesson Plan Magic

A Cowork / Claude Code plugin for K-12 teachers. Jake's Lesson Plan Magic generates weekly, daily, or unit lesson plans in your own district template, voice, and pedagogy framework — with verified research and common student-PII safeguards enabled by default.

If you cloned the source repo instead of installing a packaged plugin: `plugin/` is the plugin root. Use the repo-root `Makefile` (`make test`, `make package`) to run tests or build the distributable `.plugin` archive, or point your plugin manager at `plugin/` as the unpacked plugin directory during development.

## What it does

- **lesson-planner** — Generate weekly / daily / unit plans aligned to your standards, filled into your uploaded .docx template. Outputs are .docx files.
- **classroom-artifacts** — Agenda slides (PowerPoint), exit tickets, do-nows, and sub-ready plans, derived from the active lesson plan. Artifacts output as `.docx`, `.pptx`, or `.txt` (exit-ticket copy-paste text for Google Forms).

Both skills share one config at `~/Documents/Lesson Plan Magic/config.yaml` and one voice profile per subject.

## Install

1. Place the `.plugin` file into your Cowork plugins folder, or enable it via the plugin manager.
2. Make sure Python 3.9+ is installed. The packaged plugin auto-installs its pinned Python helper packages on first use into `~/Documents/Lesson Plan Magic/.runtime/pyXY/site-packages/`.
3. First invocation triggers a 10-20 minute onboarding interview. You can upload past lesson plans (folder drop), a standards PDF / URL, and a school calendar (`.ics` or PDF with selectable text) instead of answering every question manually.
4. Generated files go to `~/Documents/Lesson Plan Magic/outputs/` on macOS and Linux, or `%USERPROFILE%\Documents\Lesson Plan Magic\outputs\` on Windows. Throughout this plugin, paths shown as `~/Documents/...` resolve via Python's `Path.home()` — you'll see them written in POSIX form in the docs even on Windows.

## Python dependencies

Requires Python 3.9 or newer. Packaged installs do not need a manual `pip install`; the plugin bootstraps a pinned runtime automatically on first use. That bootstrap pulls from [`shared/runtime-requirements.lock.txt`](shared/runtime-requirements.lock.txt), so release smoke tests and end-user installs stay on the same dependency set. If bootstrap fails, the scripts print plain-English setup instructions rather than a traceback.

If you're working on the scripts themselves, install the dev extras instead:

```
pip install -r skills/lesson-planner/scripts/requirements-dev.txt
```

## Privacy

- Generated files are fenced to `~/Documents/Lesson Plan Magic/outputs/` by default; use the explicit `--allow-anywhere` escape hatch only when you really intend to write elsewhere.
- The write path fails closed on common student-identifying and sensitive content. The scanners cover names, SSNs, phones, email addresses, student IDs, DOB fields, home-address labels, parent/guardian contact fields, lunch-status fields, common medical-note patterns, discipline-note patterns, and IEP/504-style accommodation phrasing across markdown, `.docx`, and `.pptx` output surfaces.
- `fill_template.py` scans both the plan markdown and the template's existing `.docx` text before writing. `--skip-docx-scan` exists only as a debugging escape hatch for a known-clean legacy template.
- Differentiation is always written at the population / accommodation level ("a student with extended-time accommodation"), never by name.
- `privacy.student_data: never` and `privacy.telemetry: off` in config are not user-overridable.
- The `--allow-names` flag and `approved_names` config field only silence **bare-name** hits (teacher's own name, historical figures like Rosa Parks). Keyword-anchored hits — SSN/phone/email shapes, `Student:` / `Learner:` / `IEP:` prefixes — are **non-allowlistable**: the keyword itself is the PII indicator.
- These checks reduce risk; they are not a substitute for teacher review or legal/compliance advice.

## Cost discipline

The plan pipeline delegates to cheaper models wherever possible:

- **Haiku** — compliance checks, agenda slides, exit tickets, do-nows, sub plans, and single-cell template rewrites.
- **Sonnet** — per-day lesson drafts (parallel, one subagent per day), research-query selection, onboarding.
- **Opus** — optional final voice polish when `defaults.voice_match_level: strict` or the teacher is being observed.

See `skills/lesson-planner/references/subagent-roles.md` for the full playbook.

## Typical requests

- "Plan my week for Chemistry."
- "Daily plan for Friday in Geometry — I have an observation."
- "Plan the next unit of American Lit — 3 weeks, ending with a Socratic seminar."
- "Agenda slide for today." / "Exit ticket for Monday's Bio." / "Sub plan for Thursday."
- "Update my config." / "Add a new subject."

## Roadmap

Features under development for future releases:

- **PDF export** — Convert plans and classroom artifacts to PDF (currently outputs .docx and .pptx only). Requires LibreOffice or similar.
- **Native Google Forms export** — Create Google Forms links directly instead of producing copy-paste `.txt` prompts.
- **LMS import** — Direct import to Canvas, Schoology, or Blackboard (CSV / QTI format).
- **Class-period batching** — Generate a sub plan for all classes in one day, not just one period.

## License

MIT.
