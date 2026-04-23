#!/usr/bin/env python3
"""Cross-platform plugin packager."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SRC = REPO_ROOT / "plugin"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "jakes-lesson-plan-magic.plugin"
EXCLUDED_DIRS = {".claude", ".pytest_cache", "__pycache__", "tests"}
EXCLUDED_FILES = {".DS_Store", ".coverage"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def _ignore(_src: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in EXCLUDED_DIRS or name in EXCLUDED_FILES:
            ignored.add(name)
            continue
        if any(name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
            ignored.add(name)
    return ignored


def _zip_dir(source_dir: Path, archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            zf.write(path, path.relative_to(source_dir))


def build_plugin(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    staging_root = output_path.parent / ".plugin-build"
    if staging_root.exists():
        shutil.rmtree(staging_root)
    staging_root.mkdir(parents=True)

    plugin_stage = staging_root / "plugin"
    shutil.copytree(PLUGIN_SRC, plugin_stage, ignore=_ignore)
    shutil.copy2(REPO_ROOT / "LICENSE", plugin_stage / "LICENSE")

    if output_path.exists():
        output_path.unlink()
    _zip_dir(plugin_stage, output_path)
    shutil.rmtree(staging_root)
    return output_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Lesson Plan Magic .plugin archive.")
    ap.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output .plugin path (default: {DEFAULT_OUTPUT})",
    )
    args = ap.parse_args()
    built = build_plugin(args.output.resolve())
    print(built)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
