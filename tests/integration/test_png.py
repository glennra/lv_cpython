def test_lodepng_decodes_filesystem_image(memory_filesystem):
    import lvgl.mpy as lv

    lv.lodepng_init()
    try:
        header = lv.image_header_t()
        result = lv.image_decoder_get_info("M:/tiny.png", header)

        assert result == lv.RESULT.OK
        assert header.w == 50
        assert header.h == 50
    finally:
        lv.lodepng_deinit()


def test_lodepng_draws_decoded_pixels(memory_filesystem, lv_display):
    import lvgl.mpy as lv

    lv.lodepng_init()
    try:
        buffer = bytearray(64 * 64 * 4)
        canvas = lv.canvas(lv.screen_active())
        canvas.set_buffer(buffer, 64, 64, lv.COLOR_FORMAT.ARGB8888)
        layer = lv.layer_t()
        canvas.init_layer(layer)

        descriptor = lv.draw_image_dsc_t()
        descriptor.init()
        descriptor.src = "M:/tiny.png"
        area = lv.area_t({"x1": 0, "y1": 0, "x2": 49, "y2": 49})

        lv.draw_image(layer, descriptor, area)
        canvas.finish_layer(layer)

        pixel = canvas.get_px(25, 25)
        assert pixel.alpha == 255
        assert any((pixel.red, pixel.green, pixel.blue))
    finally:
        lv.lodepng_deinit()
