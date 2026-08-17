import pytest


def test_embedded_struct_assignment():
    import lvgl.mpy as lv

    dsc = lv.draw_line_dsc_t()
    point = lv.point_precise_t()
    point.x = 10
    point.y = 20

    dsc.p1 = point

    assert dsc.p1.x == 10
    assert dsc.p1.y == 20


def test_char_pointer_struct_field():
    import lvgl.mpy as lv

    dsc = lv.draw_label_dsc_t()
    dsc.text = "GPS sats:7"

    assert dsc.text == "GPS sats:7"


def test_char_pointer_return(lv_screen):
    import lvgl.mpy as lv

    textarea = lv.textarea(lv_screen)
    textarea.set_text("abcdef")

    result = textarea.get_text()

    assert result == "abcdef"
    assert isinstance(result, str)


@pytest.mark.parametrize(
    "data",
    [
        bytes([1, 2, 3, 4]),
        bytearray([1, 2, 3, 4]),
        memoryview(bytearray([1, 2, 3, 4])),
        memoryview(bytes([1, 2, 3, 4])),
    ],
    ids=["bytes", "bytearray", "memoryview", "readonly-memoryview"],
)
def test_buffer_pointer_struct_field(data):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    dsc = lv.image_dsc_t({
        "data_size": len(data),
        "data": data,
    })

    assert dsc._obj.data != raw._lib_lvgl.ffi.NULL
