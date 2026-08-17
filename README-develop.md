## Setup

    uv sync

## Developer shortcuts

The Makefile contains useful commands. Use `make help` or just `make` to view. 

## Fast lv_cpython generator regeneration

Changed builder/py_builder.py:

    uv run python -m builder.regenerate py

Changed builder/mpy_builder.py:

    uv run python -m builder.regenerate mpy

Changed both:

    uv run python -m builder.regenerate all

Only use the full editable reinstall when the native extension/CFFI side
must be rebuilt:

    uv pip install -e . --reinstall --no-deps


## Integration implemented

Where setup.py previously did:

    ast = pycparser.parse_file(...)
    build.ast = ast

we have replaced AST construction with:

    from builder import ast_builder
    build.ast = ast_builder.run(project_path, debug=debug)

## Tests

### All

    uv run pytest -v

### Optional, long running

    uv run pytest -m sdl
    uv run pytest -m stress
    uv run pytest -m "integration and not sdl"
    uv run pytest -m acceptance

### Generated binding check

    uv run python -m builder.check_regeneration

### Native sanitizer tests

Run lifetime and integration tests under AddressSanitizer:

    uv run python -m builder.run_sanitizers

Run the same tests under AddressSanitizer and UndefinedBehaviorSanitizer:

    uv run python -m builder.run_sanitizers --sanitizers address,undefined

The command restores a normal editable build after the sanitizer run.

### CPython 3.13 arm64 cross-build

After installing the Debian cross-toolchain and target development packages
documented in
`doc/exec-plans/arm64_cross_compilation.md`, build and validate the arm64 wheel:

    scripts/build_arm64_wheel.sh

The verified wheel is written to `dist/arm64`. Pass an alternative output
directory as the command's sole argument.
