import importlib
from pathlib import Path

from pycparser import c_parser


FS_DRIVER_SOURCE = r"""
typedef unsigned int uint32_t;
typedef int lv_fs_res_t;
typedef int lv_fs_mode_t;

typedef struct _lv_fs_drv_t {
    void *user_data;
    void *(*open_cb)(
        struct _lv_fs_drv_t *drv, const char *path, lv_fs_mode_t mode
    );
    lv_fs_res_t (*read_cb)(
        struct _lv_fs_drv_t *drv, void *file_p, void *buf,
        uint32_t btr, uint32_t *br
    );
} lv_fs_drv_t;
"""


def _generate_raw_binding(tmp_path, source):
    from builder import py_builder

    # py_builder accumulates generated fragments at module scope. Reload it
    # so this small fixture is independent of session regeneration and order.
    py_builder = importlib.reload(py_builder)
    ast = c_parser.CParser().parse(source)
    py_builder.run(str(tmp_path), ast.ext)
    return Path(tmp_path, "_raw.py").read_text(encoding="utf-8")


def test_anonymous_fs_callback_names_are_stable():
    from builder.py_builder import get_anonymous_struct_callback_name

    assert get_anonymous_struct_callback_name(
        "_lv_fs_drv_t", "open_cb"
    ) == "lv_fs_drv_open_cb_t"
    assert get_anonymous_struct_callback_name(
        "_lv_fs_drv_t", "read_cb"
    ) == "lv_fs_drv_read_cb_t"


def test_callbacks_outside_fs_driver_are_not_synthesized():
    from builder.py_builder import get_anonymous_struct_callback_name

    assert get_anonymous_struct_callback_name(
        "_lv_other_t", "open_cb"
    ) is None
    assert get_anonymous_struct_callback_name(
        "_lv_fs_drv_t", None
    ) is None


def test_anonymous_fs_callbacks_generate_typedefs_and_trampolines(tmp_path):
    generated = _generate_raw_binding(tmp_path, FS_DRIVER_SOURCE)

    for callback in ("lv_fs_drv_open_cb_t", "lv_fs_drv_read_cb_t"):
        python_name = callback.removeprefix("lv_")
        trampoline = f"__{python_name}_callback_func"
        assert f"{python_name} = Callable[" in generated
        assert (
            "@_lib_lvgl.ffi.def_extern(\n"
            f"    name='py_{callback}'\n"
            ")\n"
            f"def {trampoline}("
        ) in generated
        assert f"getattr(_lib_lvgl.lib, 'py_{callback}')" in generated

    assert "file_p = _get_py_callback_ptr(" in generated
    assert "br = _get_py_callback_ptr(" in generated


def test_anonymous_fs_callbacks_generate_struct_properties(tmp_path):
    generated = _generate_raw_binding(tmp_path, FS_DRIVER_SOURCE)

    assert "def open_cb(self) -> Optional[\"fs_drv_open_cb_t\"]:" in generated
    assert "def read_cb(self) -> Optional[\"fs_drv_read_cb_t\"]:" in generated
    assert "setattr(self._obj, 'open_cb', c_func)" in generated
    assert "setattr(self._obj, 'read_cb', c_func)" in generated


def test_model_backed_generation_matches_ast_and_repeats_cleanly(tmp_path):
    from builder import py_builder
    from builder.binding_model import build_binding_model

    py_builder = importlib.reload(py_builder)
    ast = c_parser.CParser().parse(FS_DRIVER_SOURCE)
    model = build_binding_model(ast)
    ast_output = tmp_path / "ast"
    model_output = tmp_path / "model"
    repeated_output = tmp_path / "repeated"
    ast_output.mkdir()
    model_output.mkdir()
    repeated_output.mkdir()

    py_builder.run(str(ast_output), ast.ext)
    py_builder.run(str(model_output), model)
    py_builder.run(str(repeated_output), model)

    expected = (ast_output / "_raw.py").read_bytes()
    assert (model_output / "_raw.py").read_bytes() == expected
    assert (repeated_output / "_raw.py").read_bytes() == expected
