import gc


def test_micropythonos_keyboard_map_survives_collection(lv_screen):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    keyboard_map = [
        "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "\n",
        "a", "s", "d", "f", "g", "h", "j", "k", "l", "\n",
        lv.SYMBOL.UP, "z", "x", "c", "v", "b", "n", "m",
        lv.SYMBOL.BACKSPACE, "\n",
        "?123", ",", " ", ".", lv.SYMBOL.OK, lv.SYMBOL.NEW_LINE, None,
    ]
    controls = [lv.buttonmatrix.CTRL.WIDTH_10] * len(keyboard_map)
    keyboard = lv.keyboard(lv_screen)
    keyboard.set_map(lv.keyboard.MODE.USER_1, keyboard_map, controls)
    keyboard.set_mode(lv.keyboard.MODE.USER_1)

    del keyboard_map, controls
    gc.collect()
    junk = [bytearray(1024) for _ in range(500)]
    c_map = raw._lib_lvgl.lib.lv_keyboard_get_map_array(keyboard._obj)

    assert raw._lib_lvgl.ffi.string(c_map[0]) == b"q"
    assert raw._lib_lvgl.ffi.string(c_map[10]) == b"\n"
    assert junk
