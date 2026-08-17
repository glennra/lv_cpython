def _map_strings(raw, c_map, count):
    return [raw._lib_lvgl.ffi.string(c_map[index]) for index in range(count)]


def test_buttonmatrix_map_survives_collection(lv_screen, force_collection):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    button_map = ["7", "8", "9", "/", "\n", "4", "5", "6", None]
    expected = [item.encode() for item in button_map[:-1]]
    buttonmatrix = lv.buttonmatrix(lv_screen)
    buttonmatrix.set_map(button_map)

    del button_map
    junk = force_collection()

    c_map = raw._lib_lvgl.lib.lv_buttonmatrix_get_map(buttonmatrix._obj)
    assert _map_strings(raw, c_map, len(expected)) == expected
    assert junk


def test_buttonmatrix_map_reference_is_replaced(lv_screen):
    import lvgl.mpy as lv

    buttonmatrix = lv.buttonmatrix(lv_screen)
    buttonmatrix.set_map(["old", None])
    key = lv._obj_ref_key(buttonmatrix)
    first = lv._retained_obj_refs[key]["buttonmatrix_map"]

    buttonmatrix.set_map(["new", None])
    retained = lv._retained_obj_refs[key]["buttonmatrix_map"]

    assert retained is not first
    assert list(retained) == ["new", None]


def test_recreated_buttonmatrix_owns_its_map(lv_screen):
    import lvgl.mpy as lv

    old = lv.buttonmatrix(lv_screen)
    old.set_map(["old", None])
    old_key = lv._obj_ref_key(old)
    old.delete()

    new = lv.buttonmatrix(lv_screen)
    new.set_map(["new", None])
    new_key = lv._obj_ref_key(new)

    assert old_key not in lv._retained_obj_refs or old_key == new_key
    assert list(lv._retained_obj_refs[new_key]["buttonmatrix_map"]) == [
        "new",
        None,
    ]
