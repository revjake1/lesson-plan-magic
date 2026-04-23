"""Pytest configuration: add both skills' scripts dirs to sys.path."""

import sys
from pathlib import Path

tests_dir = Path(__file__).parent
root_dir = tests_dir.parent

for relative in (
    ("shared",),
    ("skills", "lesson-planner", "scripts"),
    ("skills", "classroom-artifacts", "scripts"),
):
    scripts_dir = root_dir.joinpath(*relative)
    if scripts_dir.is_dir():
        sys.path.insert(0, str(scripts_dir))
