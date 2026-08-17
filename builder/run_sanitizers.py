"""Build the extension with sanitizers and run native lifetime tests."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


SUPPORTED_SANITIZERS = ("address", "undefined")
RUNTIME_NAMES = {
    "address": "asan",
    "undefined": "ubsan",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run(command, *, root, env):
    subprocess.run(command, cwd=root, env=env, check=True)


def _runtime_library(sanitizer, env):
    compiler = env.get("CC", "cc")
    runtime = RUNTIME_NAMES[sanitizer]
    result = subprocess.run(
        [compiler, f"-print-file-name=lib{runtime}.so"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    path = result.stdout.strip()
    if not path or path == f"lib{runtime}.so":
        raise RuntimeError(f"could not locate the {sanitizer} runtime")
    return path


def _install_command(uv, python):
    return [
        uv,
        "pip",
        "install",
        "--python",
        str(python),
        "-e",
        ".",
        "--reinstall",
        "--no-deps",
        "--no-cache",
        "--no-build-isolation",
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run lifetime and integration tests with ASan/UBSan",
    )
    parser.add_argument(
        "--sanitizers",
        default="address",
        help="comma-separated sanitizers: address, undefined",
    )
    parser.add_argument(
        "--no-restore",
        action="store_true",
        help="leave the sanitized extension installed (for ephemeral CI)",
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="pytest arguments (default: -m 'lifetime or integration')",
    )
    args = parser.parse_args(argv)

    sanitizers = tuple(
        item.strip() for item in args.sanitizers.split(",") if item.strip()
    )
    unsupported = set(sanitizers) - set(SUPPORTED_SANITIZERS)
    if not sanitizers or unsupported:
        parser.error(
            "sanitizers must contain only: "
            + ", ".join(SUPPORTED_SANITIZERS)
        )
    if sys.platform == "win32":
        parser.error("sanitizer builds are not supported on Windows")

    uv = shutil.which("uv")
    if uv is None:
        parser.error("uv is required to rebuild the editable extension")

    root = _project_root()
    venv_python = root / ".venv" / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    if not venv_python.exists():
        parser.error(".venv is missing; run `uv sync --dev` first")

    normal_env = os.environ.copy()
    normal_env.pop("LV_SANITIZERS", None)
    normal_env.setdefault("UV_CACHE_DIR", "/tmp/lv-cpython-uv-cache")
    build_env = {
        **normal_env,
        "LV_SANITIZERS": ",".join(sanitizers),
        "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
        "LSAN_OPTIONS": "detect_leaks=0",
        "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1",
    }
    runtimes = []
    if sys.platform.startswith("linux"):
        runtimes = [
            _runtime_library(sanitizer, build_env)
            for sanitizer in sanitizers
        ]
        existing = build_env.get("LD_PRELOAD")
        if existing:
            runtimes.append(existing)
        build_env["LD_PRELOAD"] = ":".join(runtimes)
    installed_sanitized = False

    try:
        _run(_install_command(uv, venv_python), root=root, env=build_env)
        installed_sanitized = True

        test_env = {
            **build_env,
            "LV_SKIP_REGENERATION": "1",
            "SDL_VIDEODRIVER": "dummy",
            "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
            "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1",
        }
        pytest_args = args.pytest_args or [
            "-m",
            "lifetime or integration",
        ]
        _run(
            [str(venv_python), "-m", "pytest", *pytest_args],
            root=root,
            env=test_env,
        )
    finally:
        if installed_sanitized and not args.no_restore:
            restore_env = {
                **normal_env,
                "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
                "LSAN_OPTIONS": "detect_leaks=0",
                "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1",
            }
            if runtimes:
                restore_env["LD_PRELOAD"] = ":".join(runtimes)
            _run(
                _install_command(uv, venv_python),
                root=root,
                env=restore_env,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
