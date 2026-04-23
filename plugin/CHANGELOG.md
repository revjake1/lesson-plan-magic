# Changelog

## 0.3.2

- Hardened Windows path resolution so both skills honor explicit home-directory overrides consistently during CLI runs and packaged installs.
- Taught classroom-artifact helpers to read locale-encoded markdown/config text cleanly instead of crashing on non-UTF-8 Windows files.
- Replaced Unicode status glyphs in `ingest_past_plans.py` with ASCII-safe console output to avoid Windows `charmap` write failures.

## 0.3.1

- Added automatic first-run Python runtime bootstrap into the Lesson Plan Magic home, so packaged installs no longer require a manual `pip install`.
- Replaced the shell-only packaging flow with cross-platform build and smoke-test scripts, and wired CI/release validation around the built `.plugin` archive.
- Tightened public/plugin docs so artifact scope, calendar behavior, output boundaries, and citation verification claims match the shipped code.
- Slimmed both skill entrypoints and split the old subagent playbook into small prompt contracts so Claude Code and Cowork load less instruction text on each run.
- Added dense `.plan.json` and `voice-profile.json` sidecars, and taught artifact generation to prefer compact structured plan/day payloads before falling back to markdown.
- Fixed the CI/release dependency install path so tagged releases validate correctly on GitHub Actions.

## 0.2.5

- Removed local Claude development settings from the release workflow and ignored `.claude/` / `.DS_Store`.
- Consolidated shared PII scanning vocabulary and matching logic into `shared/pii_common.py`.
- Clarified `--allow-names` help text and documented the `--skip-docx-scan` debugging flag.
- Replaced the private `ipaddress._BaseAddress` annotation in `safe_http.py`.
- Marked the sub-plan schema example's nearby-teacher sample as fictional.
