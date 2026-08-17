def test_import():
    import lvgl._raw  # NOQA: F401
    import lvgl.mpy  # NOQA: F401


def test_basic_binding():
    import lvgl.mpy as lv

    assert hasattr(lv, "obj")
    assert hasattr(lv, "screen_active")
    assert hasattr(lv, "group_create")
