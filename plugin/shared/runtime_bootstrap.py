#!/usr/bin/env python3
"""Auto-install packaged Python runtime deps on first use.

The packaged plugin cannot rely on Cowork / Claude Code shipping every Python
dependency on the teacher's machine. This helper installs pinned runtime
dependencies into the Lesson Plan Magic home on first use, then reuses that
local site-packages directory on subsequent runs.
"""

from __future__ import annotations

import argparse
import ensurepip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable


DISABLE_AUTO_INSTALL_ENV = "LESSON_PLAN_MAGIC_DISABLE_AUTO_INSTALL"
FORCE_RUNTIME_SYNC_ENV = "LESSON_PLAN_MAGIC_FORCE_RUNTIME_SYNC"
LOCK_FILENAME = "runtime-requirements.lock.txt"
PLUGIN_MARKER = (".claude-plugin", "plugin.json")
RUNTIME_MODULES = (
    "PIL",
    "bs4",
    "certifi",
    "charset_normalizer",
    "defusedxml",
    "docx",
    "idna",
    "lxml",
    "pptx",
    "pypdf",
    "soupsieve",
    "typing_extensions",
    "urllib3",
    "xlsxwriter",
    "yaml",
)


def _home_root() -> Path:
    override = os.environ.get("LESSON_PLAN_MAGIC_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / "Documents" / "Lesson Plan Magic"


def _plugin_root(anchor: str | Path) -> Path:
    path = Path(anchor).resolve()
    candidates = [path] + list(path.parents)
    for candidate in candidates:
        if (candidate / PLUGIN_MARKER[0] / PLUGIN_MARKER[1]).exists():
            return candidate
    raise FileNotFoundError(
        f"Could not locate plugin root from anchor: {path}"
    )


def _runtime_root(anchor: str | Path) -> Path:
    version_tag = f"py{sys.version_info.major}{sys.version_info.minor}"
    return _home_root() / ".runtime" / version_tag


def runtime_site_packages(anchor: str | Path) -> Path:
    return _runtime_root(anchor) / "site-packages"


def _manifest_path(anchor: str | Path) -> Path:
    return _runtime_root(anchor) / "manifest.json"


def _lockfile_path(anchor: str | Path) -> Path:
    return _plugin_root(anchor) / "shared" / LOCK_FILENAME


def _plugin_version(anchor: str | Path) -> str:
    plugin_json = _plugin_root(anchor) / PLUGIN_MARKER[0] / PLUGIN_MARKER[1]
    data = json.loads(plugin_json.read_text(encoding="utf-8"))
    return str(data.get("version", "unknown"))


def _expected_manifest(anchor: str | Path) -> dict[str, str]:
    lockfile = _lockfile_path(anchor)
    return {
        "lock_sha256": hashlib.sha256(lockfile.read_bytes()).hexdigest(),
        "plugin_version": _plugin_version(anchor),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
    }


def _load_manifest(anchor: str | Path) -> dict[str, str] | None:
    manifest_path = _manifest_path(anchor)
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return {str(k): str(v) for k, v in payload.items()}


def _write_manifest(anchor: str | Path) -> None:
    manifest_path = _manifest_path(anchor)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(_expected_manifest(anchor), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _module_available(module_name: str) -> bool:
    try:
        __import__(module_name)
    except Exception:
        return False
    return True


def _modules_available(module_names: Iterable[str]) -> bool:
    return all(_module_available(name) for name in module_names)


def _pip_available() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _ensure_pip() -> None:
    if _pip_available():
        return
    ensurepip.bootstrap(upgrade=True)
    if not _pip_available():
        raise RuntimeError(
            "Python pip is not available, and automatic bootstrap could not enable it."
        )


def _sync_runtime(anchor: str | Path) -> Path:
    site_packages = runtime_site_packages(anchor)
    runtime_root = _runtime_root(anchor)
    lockfile = _lockfile_path(anchor)

    if site_packages.exists():
        shutil.rmtree(site_packages)
    runtime_root.mkdir(parents=True, exist_ok=True)

    _ensure_pip()
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-warn-script-location",
        "--upgrade",
        "--target",
        str(site_packages),
        "-r",
        str(lockfile),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        tail = (result.stderr or result.stdout).strip().splitlines()[-8:]
        details = "\n".join(tail)
        raise RuntimeError(
            "Lesson Plan Magic could not install its Python helpers automatically.\n"
            "Check network access and Python/pip permissions, then retry.\n"
            f"pip output:\n{details}"
        )

    if str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    _write_manifest(anchor)
    return site_packages


def ensure_plugin_runtime(
    anchor: str | Path,
    *,
    required_modules: Iterable[str] = RUNTIME_MODULES,
) -> Path:
    """Ensure the plugin's pinned runtime is available on ``sys.path``.

    Behavior:
    - Reuse the per-user runtime if its manifest matches this plugin build.
    - If the user already has compatible packages globally available, don't
      force-install a local runtime for development/test workflows.
    - If packages are missing, install them automatically into the
      Lesson Plan Magic runtime directory.
    """

    site_packages = runtime_site_packages(anchor)
    manifest_ok = _load_manifest(anchor) == _expected_manifest(anchor)
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))

    if manifest_ok and _modules_available(required_modules):
        return site_packages

    if os.environ.get(DISABLE_AUTO_INSTALL_ENV) == "1":
        if _modules_available(required_modules):
            return site_packages
        raise RuntimeError(
            "Lesson Plan Magic Python helpers are missing and automatic install is disabled."
        )

    force_sync = os.environ.get(FORCE_RUNTIME_SYNC_ENV) == "1"
    if not force_sync:
        if site_packages.exists():
            return _sync_runtime(anchor)
        if _modules_available(required_modules):
            return site_packages

    synced_path = _sync_runtime(anchor)
    if not _modules_available(required_modules):
        raise RuntimeError(
            "Lesson Plan Magic installed its runtime helpers, but imports still failed."
    )
    return synced_path


def _bootstrap_failure_message(exc: Exception) -> str:
    home_root = _home_root()
    return (
        "Lesson Plan Magic could not prepare its Python helper runtime.\n"
        f"{exc}\n\n"
        "What this plugin requires:\n"
        "- Python 3.9 or newer installed on this computer\n"
        f"- Permission to create files under {home_root}\n"
        "- Normal internet access on first run so the helper packages can be installed\n\n"
        "What to do next:\n"
        "- If Python is missing, install it from https://python.org and restart Cowork or Claude Code\n"
        "- If your network blocks package downloads, allow PyPI access or ask IT to preinstall Python package access\n"
        "- Then run the plugin again; it will retry the helper install automatically"
    )


def ensure_plugin_runtime_or_exit(
    anchor: str | Path,
    *,
    required_modules: Iterable[str] = RUNTIME_MODULES,
) -> Path:
    """CLI-friendly wrapper: print a plain-English setup error and exit."""
    try:
        return ensure_plugin_runtime(anchor, required_modules=required_modules)
    except (RuntimeError, FileNotFoundError) as exc:
        print(_bootstrap_failure_message(exc), file=sys.stderr)
        raise SystemExit(1) from exc


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync Lesson Plan Magic runtime deps.")
    ap.add_argument(
        "--anchor",
        required=True,
        help="Path inside the plugin (typically a script file) used to locate the plugin root.",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON describing the resolved runtime path.",
    )
    args = ap.parse_args()

    site_packages = ensure_plugin_runtime(args.anchor)
    payload = {
        "site_packages": str(site_packages),
        "manifest": str(_manifest_path(args.anchor)),
    }
    if args.json:
        print(json.dumps(payload))
    else:
        print(payload["site_packages"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
