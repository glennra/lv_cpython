from pathlib import Path

import pytest


@pytest.fixture
def ttf_data():
    root = Path(__file__).resolve().parents[2]
    return (
        root / "src/lvgl/scripts/built_in_font/unscii-8.ttf"
    ).read_bytes()


def test_tiny_ttf_from_memory(lv, ttf_data):
    font = lv.tiny_ttf_create_data(ttf_data, len(ttf_data), 16)
    try:
        assert font is not None
        assert font.get_line_height() > 0
    finally:
        lv.tiny_ttf_destroy(font)


def test_tiny_ttf_from_filesystem(memory_filesystem):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    handles_before = len(raw._callback_object_handles)
    font = lv.tiny_ttf_create_file("M:/test.ttf", 16)
    try:
        assert font is not None
        assert font.get_line_height() > 0
        assert len(raw._callback_object_handles) == handles_before + 1
    finally:
        lv.tiny_ttf_destroy(font)

    assert len(raw._callback_object_handles) == handles_before


def test_builtin_font_get_glyph_dsc(lv):
    import lvgl._raw as raw

    font = lv.font_montserrat_14
    descriptor = lv.font_glyph_dsc_t()

    result = font.get_glyph_dsc(font, descriptor, ord("A"), 0)

    assert type(font) is raw.font_t
    assert result
    assert descriptor.adv_w > 0


def test_tiny_ttf_get_glyph_dsc(lv, ttf_data):
    font = lv.tiny_ttf_create_data(ttf_data, len(ttf_data), 16)
    try:
        descriptor = lv.font_glyph_dsc_t()
        result = font.get_glyph_dsc(font, descriptor, ord("A"), 0)

        assert type(font) is lv.font_t
        assert result
        assert descriptor.adv_w > 0
    finally:
        lv.tiny_ttf_destroy(font)
