# -*- coding: utf-8 -*-

"""Fast regeneration of lv_cpython generated Python files.

Examples, from repository root:

    uv run python -m builder.regenerate py
    uv run python -m builder.regenerate mpy
    uv run python -m builder.regenerate all

"py" regenerates lvgl/_raw.py from LVGL headers.
"mpy" regenerates lvgl/mpy.py from the already-built lvgl module.
"all" runs both in that order.

No setuptools build or C extension compilation is performed.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from collections.abc import Iterable

from . import ast_builder, binding_model, mpy_builder, py_builder


def _newest_mtime(paths: Iterable[Path]) -> int:
    newest = 0

    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    newest = max(newest, child.stat().st_mtime_ns)
        elif path.exists():
            newest = max(newest, path.stat().st_mtime_ns)

    return newest


def _is_stale(target: Path, dependencies: Iterable[Path]) -> bool:
    if not target.exists():
        return True

    return target.stat().st_mtime_ns < _newest_mtime(dependencies)

def _project_path() -> Path:
    return Path(__file__).resolve().parent.parent

def _lvgl_headers(root: Path):
    yield from (root / "lvgl").rglob("*.h")

def regenerate_py(
    root: Path,
    *,
    debug: bool = False,
    force: bool = False,
) -> None:
    target = root / "lvgl" / "_raw.py"

    dependencies = [
        root / "builder" / "py_builder.py",
        root / "builder" / "binding_model.py",
        root / "builder" / "lvgl.template.py",
        root / "src" / "lv_conf.h",
        *_lvgl_headers(root),
    ]

    if not force and not _is_stale(target, dependencies):
        print(f"{target}: up to date")
        return

    print(f"Regenerating {target}")

    output_path = root / "lvgl"
    output_path.mkdir(parents=True, exist_ok=True)

    print("Parsing LVGL headers...")
    ast = ast_builder.run(root, debug=debug)
    model = binding_model.build_binding_model(ast)

    print(f"Generating {output_path / '_raw.py'}...")
    py_builder.run(str(output_path), model)

def regenerate_mpy(
    root: Path,
    *,
    debug: bool = False,
    force: bool = False,
) -> None:
    target = root / "lvgl" / "mpy.py"

    dependencies = [
        root / "builder" / "mpy_builder.py",
        root / "builder" / "binding_model.py",
        root / "builder" / "raw_api_model.py",
        root / "lvgl" / "_raw.py",
        root / "src" / "lvgl" / "src" / "font" / "lv_symbol_def.h",
        *_lvgl_headers(root),
    ]

    if not force and not _is_stale(target, dependencies):
        print(f"{target}: up to date")
        return

    print(f"Regenerating {target}")

    root_str = str(root)

    print("Parsing LVGL headers...")
    ast = ast_builder.run(root, debug=debug)
    model = binding_model.build_binding_model(
        ast,
        symbol_header=root / "src/lvgl/src/font/lv_symbol_def.h",
    )

    print(f"Generating {root / 'lvgl' / 'mpy.py'}...")
    mpy_builder.run(root_str, model)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate lv_cpython Python binding files without rebuilding extension."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=("py", "mpy", "all"),
        help="generated file(s) to rebuild (default: all)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="pass debug preprocessing flags while building AST",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="regenerate even when generated files appear up to date",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="lv_cpython repository root (normally auto-detected)",
    )

    args = parser.parse_args(argv)

    root = (
        args.project_root.expanduser().resolve()
        if args.project_root is not None
        else _project_path()
    )

    if not (root / "builder").is_dir():
        parser.error(f"not an lv_cpython repository root: {root}")

    old_cwd = Path.cwd()
    try:
        # setup.py uses several relative paths. Keeping cwd at repo root also
        # makes generator behavior deterministic.
        os.chdir(root)

        if args.target in ("py", "all"):
            regenerate_py(root, debug=args.debug, force=args.force)

        if args.target in ("mpy", "all"):
            regenerate_mpy(root, force=args.force)
    finally:
        os.chdir(old_cwd)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
