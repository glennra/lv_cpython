def test_canvas_buffer_survives_collection(lv_screen, force_collection):
    import lvgl.mpy as lv

    canvas = lv.canvas(lv_screen)
    buffer = bytearray(8 * 8 * 2)
    canvas.set_buffer(buffer, 8, 8, lv.COLOR_FORMAT.RGB565)

    del buffer
    junk = force_collection()
    canvas.fill_bg(lv.color_hex(0xFF0000), lv.OPA.COVER)

    retained = lv._retained_obj_refs[lv._obj_ref_key(canvas)]["canvas_buffer"]
    pixel = canvas.get_px(4, 4)
    assert pixel.red == 255
    assert pixel.green == 0
    assert pixel.blue == 0
    assert pixel.alpha == 255
    assert any(retained)
    assert junk


def test_replacing_canvas_buffer_replaces_retained_reference(lv_screen):
    import lvgl.mpy as lv

    canvas = lv.canvas(lv_screen)
    first = bytearray(8 * 8 * 2)
    second = bytearray(8 * 8 * 2)
    canvas.set_buffer(first, 8, 8, lv.COLOR_FORMAT.RGB565)
    canvas.set_buffer(second, 8, 8, lv.COLOR_FORMAT.RGB565)

    retained = lv._retained_obj_refs[lv._obj_ref_key(canvas)]["canvas_buffer"]
    assert retained is second
