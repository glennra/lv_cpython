def test_flat_constants():
    import lvgl._raw as raw
    import lvgl.mpy as lv

    assert hasattr(lv, "RADIUS_CIRCLE")
    assert hasattr(lv, "IMAGE_HEADER_MAGIC")
    assert hasattr(lv, "GRID_CONTENT")
    assert hasattr(lv, "GRID_TEMPLATE_LAST")
    assert int(lv.RADIUS_CIRCLE) == int(raw.RADIUS_CIRCLE)
    assert int(lv.IMAGE_HEADER_MAGIC) == int(raw.IMAGE_HEADER_MAGIC)
    assert int(lv.GRID_CONTENT) == int(raw.GRID_CONTENT)
    assert int(lv.GRID_TEMPLATE_LAST) == int(raw.GRID_TEMPLATE_LAST)
    assert int(lv.GRID.CONTENT) == int(raw.GRID_CONTENT)
    assert int(lv.GRID.TEMPLATE_LAST) == int(raw.GRID_TEMPLATE_LAST)


def test_grouped_constants_remain_namespaced():
    import lvgl._raw as raw
    import lvgl.mpy as lv

    assert int(lv.ALIGN.CENTER) == int(raw.ALIGN_CENTER)
    assert int(lv.STATE.CHECKED) == int(raw.STATE_CHECKED)
    assert int(lv.PART.MAIN) == int(raw.PART_MAIN)
