#!/usr/bin/env python3
"""Smoke-test the packaged plugin from a clean Python environment."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile


def _run(cmd: list[str], *, env: dict[str, str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
    if result.returncode == 0:
        return
    raise RuntimeError(
        f"Command failed: {' '.join(cmd)}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def smoke_test(plugin_archive: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="lpm-smoke-") as td:
        temp_root = Path(td)
        extracted = temp_root / "plugin"
        extracted.mkdir()
        with zipfile.ZipFile(plugin_archive) as zf:
            zf.extractall(extracted)

        home_root = temp_root / "lesson-plan-magic-home"
        venv_dir = temp_root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)

        if os.name == "nt":
            python_bin = venv_dir / "Scripts" / "python.exe"
        else:
            python_bin = venv_dir / "bin" / "python"

        env = os.environ.copy()
        env["LESSON_PLAN_MAGIC_HOME"] = str(home_root)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

        lesson_scripts = extracted / "skills" / "lesson-planner" / "scripts"
        artifact_scripts = extracted / "skills" / "classroom-artifacts" / "scripts"

        _run([str(python_bin), str(lesson_scripts / "fill_template.py"), "--help"], env=env)
        _run([str(python_bin), str(lesson_scripts / "verify_research.py"), "--help"], env=env)
        _run([str(python_bin), str(artifact_scripts / "generate_agenda_slide.py"), "--help"], env=env)
        _run(
            [
                str(python_bin),
                "-c",
                (
                    "import sys; "
                    f"sys.path.insert(0, {str((extracted / 'shared')).__repr__()}); "
                    "from runtime_bootstrap import runtime_site_packages; "
                    f"anchor={str(lesson_scripts / 'fill_template.py').__repr__()}; "
                    "print(runtime_site_packages(anchor))"
                ),
            ],
            env=env,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Smoke-test a packaged Lesson Plan Magic plugin.")
    ap.add_argument("plugin_archive", type=Path)
    args = ap.parse_args()
    smoke_test(args.plugin_archive.resolve())
    print("smoke-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
