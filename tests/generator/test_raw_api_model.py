from pathlib import Path

from builder.raw_api_model import RawClass, RawFunction, parse_raw_api


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_static_raw_api_extracts_signatures_and_class_relationships():
    model = parse_raw_api(PROJECT_ROOT / "lvgl/_raw.py")
    exports = dict(model.items())

    snprintf = exports["snprintf"]
    assert isinstance(snprintf, RawFunction)
    assert tuple(snprintf.signature.parameters) == (
        "buffer",
        "count",
        "format",
        "args",
    )
    assert snprintf.signature.parameters["args"].kind.name == "VAR_POSITIONAL"

    area = exports["area_t"]
    assert isinstance(area, RawClass)
    assert model.class_is_subclass(area, "_StructUnion")


def test_static_raw_api_preserves_export_order():
    model = parse_raw_api(PROJECT_ROOT / "lvgl/_raw.py")
    names = [name for name, _ in model.items()]

    assert names.index("tick_get") < names.index("display_create")
    assert names.index("area_t") < names.index("event_t")
