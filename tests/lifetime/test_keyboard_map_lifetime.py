def _map_strings(raw, c_map, count):
    ffi = raw._lib_lvgl.ffi
    return [ffi.string(c_map[index]) for index in range(count)]


def test_keyboard_map_survives_collection(lv_screen, force_collection):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    keyboard_map = [
        "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "\n",
        "a", "s", "d", "f", "g", "h", "j", "k", "l", "\n",
        "z", "x", "c", "v", "b", "n", "m", None,
    ]
    expected = [item.encode() for item in keyboard_map[:-1]]
    ctrl_map = [0] * len(keyboard_map)
    keyboard = lv.keyboard(lv_screen)
    keyboard.set_map(lv.keyboard.MODE.USER_1, keyboard_map, ctrl_map)
    keyboard.set_mode(lv.keyboard.MODE.USER_1)

    del keyboard_map, ctrl_map
    junk = force_collection()

    c_map = raw._lib_lvgl.lib.lv_keyboard_get_map_array(keyboard._obj)
    assert _map_strings(raw, c_map, len(expected)) == expected
    assert junk


def test_keyboard_maps_are_retained_per_mode_and_replaced(lv_screen):
    import lvgl.mpy as lv

    keyboard = lv.keyboard(lv_screen)
    keyboard.set_map(lv.keyboard.MODE.USER_1, ["one", None], [0, 0])
    key = lv._obj_ref_key(keyboard)
    first = lv._retained_obj_refs[key]["keyboard_map_4"]

    keyboard.set_map(lv.keyboard.MODE.USER_2, ["two", None], [0, 0])
    keyboard.set_map(lv.keyboard.MODE.USER_1, ["new", None], [0, 0])
    refs = lv._retained_obj_refs[key]

    assert "keyboard_map_4" in refs
    assert "keyboard_ctrl_map_4" in refs
    assert "keyboard_map_5" in refs
    assert "keyboard_ctrl_map_5" in refs
    assert refs["keyboard_map_4"] is not first
