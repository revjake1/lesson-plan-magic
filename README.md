# Jake's Lesson Plan Magic Source Repo

This repository packages the Lesson Plan Magic plugin from the `extracted/` directory. That directory is the plugin root: it contains `.claude-plugin/plugin.json`, the two skills, shared assets, and the test suite.

Use the repo like this:

- Local development: work inside `extracted/`
- Tests: run `make test`
- Packaging: run `make package` to build `dist/jakes-lesson-plan-magic.plugin`

Quick start:

```bash
python3 -m venv .venv
.venv/bin/pip install -r extracted/skills/lesson-planner/scripts/requirements-dev.txt
make test
make package
```

Repo layout:

- `extracted/.claude-plugin/plugin.json`: plugin manifest
- `extracted/skills/lesson-planner`: planner skill, scripts, assets, references
- `extracted/skills/classroom-artifacts`: agenda/exit-ticket/do-now/sub-plan skill
- `extracted/tests`: pytest suite

The packaged `.plugin` archive should contain the contents of `extracted/`, not the `extracted/` folder itself, and should exclude dev-only files like `tests/`, `.pytest_cache/`, `.coverage`, and `.DS_Store`.
