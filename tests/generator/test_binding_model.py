import builtins
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from pycparser import c_parser

from builder import ast_builder
from builder.binding_model import (
    VA_LIST_REASON,
    build_binding_model,
    filter_unsupported_declarations,
)


MODEL_SOURCE = r"""
typedef char *va_list;
typedef unsigned int uint32_t;

typedef void (*lv_event_cb_t)(void *event);

typedef struct lv_widget_t {
    int value;
    lv_event_cb_t event_cb;
} lv_widget_t;

typedef enum lv_mode_t {
    LV_MODE_OFF = 0,
    LV_MODE_ON
} lv_mode_t;

extern const uint32_t LV_MAGIC;

lv_widget_t *lv_widget_create(lv_widget_t *parent);
void lv_widget_set_value(lv_widget_t *widget, int value);
int lv_snprintf(char *buffer, uint32_t count, const char *format, ...);
int lv_vsnprintf(
    char *buffer, uint32_t count, const char *format, va_list args
);
"""


def _synthetic_ast():
    return c_parser.CParser().parse(MODEL_SOURCE)


def test_model_extracts_architecture_neutral_declarations(tmp_path):
    symbol_header = tmp_path / "lv_symbol_def.h"
    symbol_header.write_text(
        '#define LV_SYMBOL_AUDIO "\\xEF\\x80\\x81"\n',
        encoding="utf-8",
    )

    model = build_binding_model(
        _synthetic_ast(),
        symbol_header=symbol_header,
    )

    functions = {function.c_name: function for function in model.functions}
    assert functions["lv_snprintf"].variadic is True
    assert functions["lv_widget_set_value"].method_owner == "widget"
    assert functions["lv_widget_set_value"].method_name == "set_value"
    assert functions["lv_widget_set_value"].parameters[0].type.spelling == (
        "lv_widget_t *"
    )

    aggregate = next(
        item for item in model.aggregates if item.c_name == "lv_widget_t"
    )
    assert aggregate.kind == "struct"
    assert [(field.name, field.type.spelling) for field in aggregate.fields] == [
        ("value", "int"),
        ("event_cb", "lv_event_cb_t"),
    ]

    callback = next(
        item for item in model.typedefs if item.c_name == "lv_event_cb_t"
    )
    assert callback.callback is True
    assert callback.target.kind == "pointer"

    enum = next(item for item in model.enums if item.c_name == "lv_mode_t")
    assert [(member.c_name, member.value) for member in enum.members] == [
        ("LV_MODE_OFF", "0"),
        ("LV_MODE_ON", None),
    ]
    assert [constant.c_name for constant in model.constants] == ["LV_MAGIC"]
    assert model.symbols[0].name == "AUDIO"
    assert model.symbols[0].value == "\uf001"


def test_model_is_immutable():
    model = build_binding_model(_synthetic_ast())

    with pytest.raises(FrozenInstanceError):
        model.functions[0].python_name = "changed"


def test_model_build_does_not_import_runtime_bindings(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "cffi" or name == "lvgl" or name.startswith("lvgl."):
            raise AssertionError(f"runtime import attempted: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    model = build_binding_model(_synthetic_ast())

    assert "lv_widget_create" in {
        function.c_name for function in model.functions
    }


def test_unsupported_policy_reports_reason_and_keeps_variadic_api():
    ast, exclusions = filter_unsupported_declarations(_synthetic_ast())
    declarations = {
        node.name for node in ast.ext if getattr(node, "name", None)
    }

    assert "lv_vsnprintf" not in declarations
    assert "lv_snprintf" in declarations
    assert len(exclusions) == 1
    assert exclusions[0].c_name == "lv_vsnprintf"
    assert exclusions[0].reason == VA_LIST_REASON


def test_real_lvgl_headers_populate_representative_model():
    root = Path(__file__).resolve().parents[2]
    ast = ast_builder.run(root, include_unsupported=True)
    model = build_binding_model(
        ast,
        symbol_header=root / "src/lvgl/src/font/lv_symbol_def.h",
    )

    functions = {function.c_name: function for function in model.functions}
    assert "lv_tick_get" in functions
    assert functions["lv_snprintf"].variadic is True
    assert functions["lv_label_set_text"].method_owner == "label"
    assert functions["lv_label_set_text"].method_name == "set_text"

    exclusions = {item.c_name: item.reason for item in model.exclusions}
    assert exclusions["lv_vsnprintf"] == VA_LIST_REASON
    assert exclusions["lv_label_set_text_vfmt"] == VA_LIST_REASON

    assert any(item.c_name == "lv_area_t" for item in model.aggregates)
    assert any(item.c_name == "lv_event_cb_t" for item in model.typedefs)
    assert any(
        item.name == "AUDIO" and item.value == "\uf001"
        for item in model.symbols
    )
