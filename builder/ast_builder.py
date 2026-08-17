# -*- coding: utf-8 -*-

"""Build the pycparser AST used by lv_cpython's Python binding generator.

This module contains only preprocessing/parsing.  It does not invoke
setuptools, CFFI compilation, wheel building, or package installation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pycparser
from .binding_model import filter_unsupported_declarations


def _remove_va_list_functions(ast):
    """Backward-compatible wrapper for the centralized declaration policy."""
    return filter_unsupported_declarations(ast)[0]


def _project_path() -> Path:
    return Path(__file__).resolve().parent.parent


def _cpp_config(debug: bool = False) -> tuple[str, list[str], str]:
    """Return (cpp executable, cpp args, include-path environment key)."""
    cpp_args = ["-DCPYTHON_SDL"]

    if sys.platform.startswith("win"):
        cpp_path = "cl"
        include_path_env_key = "INCLUDE"
        cpp_args.insert(0, "-std:c11")
        cpp_args.extend([
            "/wd4996",
            "/wd4244",
            "/wd4267",
        ])
        if debug:
            cpp_args.append("/Zi")

    elif sys.platform.startswith("darwin"):
        cpp_path = "clang"
        include_path_env_key = "C_INCLUDE_PATH"
        cpp_args.insert(0, "-std=c11")
        if debug:
            cpp_args.append("-ggdb")

    else:
        cpp_path = "gcc"
        include_path_env_key = "C_INCLUDE_PATH"
        cpp_args.insert(0, "-std=c11")
        cpp_args.append("-Wno-incompatible-pointer-types")
        if debug:
            cpp_args.append("-ggdb")

    return cpp_path, cpp_args, include_path_env_key


def run(
    project_path: str | os.PathLike[str] | None = None,
    *,
    debug: bool = False,
    include_unsupported: bool = False,
):
    """Parse LVGL headers and return pycparser AST."""
    root = Path(project_path).resolve() if project_path else _project_path()

    fake_libc_path = root / "builder" / "fake_libc_include"
    lvgl_header_path = root / "src" / "lvgl" / "demos" / "lv_demos.h"

    if not fake_libc_path.is_dir():
        raise FileNotFoundError(f"fake libc include directory not found: {fake_libc_path}")

    if not lvgl_header_path.is_file():
        raise FileNotFoundError(f"LVGL header not found: {lvgl_header_path}")

    cpp_path, cpp_args, include_path_env_key = _cpp_config(debug)

    # setup.py prepends fake_libc_include to the compiler include-search
    # environment while pycparser runs.  Preserve and restore user's value.
    old_include_path = os.environ.get(include_path_env_key)
    fake_prefix = str(fake_libc_path)

    if old_include_path:
        os.environ[include_path_env_key] = (
            fake_prefix + os.pathsep + old_include_path
        )
    else:
        os.environ[include_path_env_key] = fake_prefix + os.pathsep

    try:
        ast = pycparser.parse_file(
            str(lvgl_header_path),
            use_cpp=True,
            cpp_path=cpp_path,
            cpp_args=cpp_args + [
                "-E",
                "-DPYCPARSER",
                f'-I"{fake_libc_path}"',
            ],
            parser=None,
        )
        if include_unsupported:
            return ast
        return filter_unsupported_declarations(ast)[0]
    finally:
        if old_include_path is None:
            os.environ.pop(include_path_env_key, None)
        else:
            os.environ[include_path_env_key] = old_include_path
