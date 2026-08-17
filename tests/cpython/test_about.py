def test_about_style_runtime_information_screen(lv_screen):
    import lvgl.mpy as lv

    rows = [
        f"LVGL version: {lv.version_major()}."
        f"{lv.version_minor()}.{lv.version_patch()}",
        f"Binding version: {lv.binding_version()}",
        f"Display: {lv_screen.get_display().get_horizontal_resolution()}x"
        f"{lv_screen.get_display().get_vertical_resolution()}",
    ]

    labels = []
    for text in rows:
        label = lv.label(lv_screen)
        label.set_text(text)
        labels.append(label)

    assert labels[0].get_text().startswith("LVGL version: ")
    assert labels[1].get_text() == f"Binding version: {lv.binding_version()}"
    assert labels[2].get_text() == "Display: 320x240"
