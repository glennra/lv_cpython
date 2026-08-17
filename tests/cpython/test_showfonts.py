def test_showfonts_builtin_and_tiny_ttf_glyphs(memory_filesystem):
    import lvgl.mpy as lv

    tiny_font = lv.tiny_ttf_create_file("M:/test.ttf", 16)
    try:
        for font in (lv.font_montserrat_14, tiny_font):
            descriptor = lv.font_glyph_dsc_t()
            result = font.get_glyph_dsc(
                font,
                descriptor,
                ord("A"),
                ord("B"),
            )

            assert result
            assert descriptor.adv_w > 0

        assert tiny_font.get_line_height() > 0
    finally:
        lv.tiny_ttf_destroy(tiny_font)
