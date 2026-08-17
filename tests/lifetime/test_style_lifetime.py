import weakref


def test_attached_style_survives_collection(lv_screen, force_collection):
    import lvgl.mpy as lv

    obj = lv.obj(lv_screen)

    def add_style():
        style = lv.style_t()
        style.init()
        style.set_radius(17)
        obj.add_style(style, 0)

    add_style()
    junk = force_collection()

    assert obj.get_style_radius(0) == 17
    assert junk


def test_remove_style_all_releases_retained_styles(lv_screen):
    import gc
    import lvgl.mpy as lv

    obj = lv.obj(lv_screen)
    style = lv.style_t()
    style.init()
    obj.add_style(style, 0)
    reference = weakref.ref(style)
    key = lv._obj_ref_key(obj)

    del style
    obj.remove_style_all()
    gc.collect()

    assert "styles" not in lv._retained_obj_refs.get(key, {})
    assert reference() is None
