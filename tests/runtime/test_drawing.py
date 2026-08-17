import pytest


def test_draw_functions_remain_module_level():
    import lvgl.mpy as lv

    assert hasattr(lv, "draw_rect")
    assert hasattr(lv, "draw_line")
    assert not hasattr(lv.draw_layer, "rect")


@pytest.mark.parametrize(
    "buffer",
    [
        bytes(8 * 8 * 2),
        bytearray(8 * 8 * 2),
        memoryview(bytearray(8 * 8 * 2)),
    ],
    ids=["bytes", "bytearray", "memoryview"],
)
def test_canvas_set_buffer_accepts_python_buffers(lv_screen, buffer):
    import lvgl.mpy as lv

    canvas = lv.canvas(lv_screen)
    canvas.set_buffer(buffer, 8, 8, lv.COLOR_FORMAT.RGB565)

    assert canvas.get_draw_buf() is not None
    retained = lv._retained_obj_refs[lv._obj_ref_key(canvas)]
    assert retained["canvas_buffer"] is buffer


def test_draw_rect_on_canvas_layer(lv_screen):
    import lvgl.mpy as lv

    buffer = bytearray(32 * 32 * 4)
    canvas = lv.canvas(lv_screen)
    canvas.set_buffer(buffer, 32, 32, lv.COLOR_FORMAT.ARGB8888)
    layer = lv.layer_t()
    canvas.init_layer(layer)

    descriptor = lv.draw_rect_dsc_t()
    descriptor.init()
    descriptor.bg_color = lv.color_hex(0xFF0000)
    descriptor.bg_opa = lv.OPA.COVER
    area = lv.area_t({"x1": 2, "y1": 2, "x2": 20, "y2": 20})

    lv.draw_rect(layer, descriptor, area)
    canvas.finish_layer(layer)

    inside = canvas.get_px(5, 5)
    outside = canvas.get_px(25, 25)
    assert inside.red == 255
    assert inside.green == 0
    assert inside.blue == 0
    assert inside.alpha == 255
    assert outside.alpha == 0
