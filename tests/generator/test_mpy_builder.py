import builtins
from pathlib import Path
import shutil

import pytest

from builder import mpy_builder
from builder import ast_builder
from builder.binding_model import build_binding_model


PROJECT_ROOT = Path(__file__).resolve().parents[2]
@pytest.fixture(scope="module")
def binding_model():
    ast = ast_builder.run(PROJECT_ROOT)
    return build_binding_model(
        ast,
        symbol_header=(
            PROJECT_ROOT / "src/lvgl/src/font/lv_symbol_def.h"
        ),
    )


@pytest.fixture(scope="module")
def generated_bindings(binding_model):
    """Run the static generator and return both API layers."""
    mpy_builder.run(str(PROJECT_ROOT), binding_model)
    return {
        "mpy": (PROJECT_ROOT / "lvgl" / "mpy.py").read_text(
            encoding="utf-8"
        ),
        "raw": (PROJECT_ROOT / "lvgl" / "_raw.py").read_text(
            encoding="utf-8"
        ),
    }


def test_generation_does_not_need_a_native_extension(
    tmp_path,
    binding_model,
    monkeypatch,
):
    package = tmp_path / "lvgl"
    package.mkdir()
    shutil.copyfile(PROJECT_ROOT / "lvgl/_raw.py", package / "_raw.py")

    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "cffi" or name == "lvgl" or name.startswith("lvgl."):
            raise AssertionError(f"runtime import attempted: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert not tuple(tmp_path.glob("**/__lib_lvgl*"))
    mpy_builder.run(str(tmp_path), binding_model)

    generated = (package / "mpy.py").read_text(encoding="utf-8")
    assert generated
    assert "class label(obj):" in generated
    assert "def tick_get() -> _lvgl.uint32_t:" in generated


def test_symbol_header_falls_back_to_project_sources(tmp_path):
    symbol_header = mpy_builder._find_symbol_header(str(tmp_path))

    assert symbol_header.endswith("src/lvgl/src/font/lv_symbol_def.h")


def test_generated_bindings_are_non_empty(generated_bindings):
    assert generated_bindings["mpy"]
    assert generated_bindings["raw"]


def test_generated_mpy_representative_api_surface(generated_bindings):
    mpy = generated_bindings["mpy"]
    raw = generated_bindings["raw"]

    # Module-level function and ordinary C variadic function.
    assert "def tick_get() -> _lvgl.uint32_t:" in mpy
    assert (
        "def snprintf(buffer: _lvgl.char, count: _lvgl.size_t, "
        "format: _lvgl.char, *args) -> _lvgl.int_:"
    ) in mpy

    # Object constructor and method placement.
    assert "class label(obj):" in mpy
    assert "def __init__(self, parent: _lvgl.obj_t = None):" in mpy
    assert "def set_text(self, text: _lvgl.char) -> None:" in mpy

    # Callback, enum, flat constant, and decoded header symbol.
    assert "event_cb_t = _lvgl.event_cb_t" in mpy
    assert "class EVENT:" in mpy
    assert "IMAGE_HEADER_MAGIC = _lvgl.IMAGE_HEADER_MAGIC" in mpy
    assert "class SYMBOL:" in mpy
    assert "    AUDIO = '\\uf001'" in mpy

    # Struct identity is retained by mpy.py and its field is present in raw.
    assert "class area_t(_lvgl.area_t):" in mpy
    assert "def x1(self) -> \"int32_t\":" in raw

    # va_list cannot be represented portably and must be absent in both APIs.
    for unsupported_name in ("vsnprintf", "label_set_text_vfmt"):
        assert f"def {unsupported_name}(" not in raw
        assert f"def {unsupported_name}(" not in mpy
