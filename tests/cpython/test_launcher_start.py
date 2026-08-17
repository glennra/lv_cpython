def test_launcher_icon_builds_and_wraps_as_image(
    memory_filesystem,
    lv_display,
):
    import lvgl.mpy as lv

    lv.lodepng_init()
    try:
        screen = lv.screen_active()
        container = lv.obj(screen)
        icon = lv.image(container)
        icon.set_src("M:/tiny.png")

        wrapped_icon = container.get_child(0)

        assert isinstance(wrapped_icon, lv.image)
        assert hasattr(wrapped_icon, "get_src")
        splash_icon = lv.image(screen)
        splash_icon.set_src(wrapped_icon.get_src())
        assert splash_icon.get_src() is not None
    finally:
        lv.lodepng_deinit()
