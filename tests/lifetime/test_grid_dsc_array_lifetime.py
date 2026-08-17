def test_grid_descriptor_arrays_survive_collection(lv_screen, force_collection):
    import lvgl.mpy as lv

    grid = lv.obj(lv_screen)
    columns = [80, 80, lv.GRID_TEMPLATE_LAST]
    rows = [60, 60, lv.GRID_TEMPLATE_LAST]
    grid.set_grid_dsc_array(columns, rows)

    del columns
    del rows
    junk = force_collection()

    retained = lv._retained_obj_refs[lv._obj_ref_key(grid)]
    assert list(retained["grid_columns"]) == [80, 80, lv.GRID_TEMPLATE_LAST]
    assert list(retained["grid_rows"]) == [60, 60, lv.GRID_TEMPLATE_LAST]
    assert int(retained["grid_columns"]._obj[2]) == lv.GRID_TEMPLATE_LAST
    assert int(retained["grid_rows"]._obj[2]) == lv.GRID_TEMPLATE_LAST
    assert junk


def test_replacing_grid_descriptors_replaces_retained_arrays(lv_screen):
    import lvgl.mpy as lv

    grid = lv.obj(lv_screen)
    grid.set_grid_dsc_array(
        [80, lv.GRID_TEMPLATE_LAST],
        [60, lv.GRID_TEMPLATE_LAST],
    )
    key = lv._obj_ref_key(grid)
    first_columns = lv._retained_obj_refs[key]["grid_columns"]
    first_rows = lv._retained_obj_refs[key]["grid_rows"]

    grid.set_grid_dsc_array(
        [40, lv.GRID_TEMPLATE_LAST],
        [30, lv.GRID_TEMPLATE_LAST],
    )
    retained = lv._retained_obj_refs[key]

    assert retained["grid_columns"] is not first_columns
    assert retained["grid_rows"] is not first_rows
