def test_child_is_wrapped_as_concrete_type(lv_screen):
    import lvgl.mpy as lv

    lv.image(lv_screen)

    child = lv_screen.get_child(0)

    assert isinstance(child, lv.image)
    assert hasattr(child, "get_src")


def test_same_lvgl_object_has_same_identity(lv_screen):
    import lvgl.mpy as lv

    lv.image(lv_screen)

    child1 = lv_screen.get_child(0)
    child2 = lv_screen.get_child(0)

    assert child1 == child2
    assert hash(child1) == hash(child2)
    assert child1 != lv.image(lv_screen)
