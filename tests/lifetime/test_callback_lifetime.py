def test_timer_callback_survives_collection(lv, force_collection):
    calls = []
    before = len(lv._global_cb_store)

    def create_timer():
        def callback(timer):
            calls.append(timer)

        return lv.timer_create(callback, 1, None)

    timer = create_timer()
    assert len(lv._global_cb_store) == before + 1
    timer.ready()
    junk = force_collection()
    lv.timer_handler()
    timer.delete()

    assert len(calls) == 1
    assert len(lv._global_cb_store) == before
    assert junk


def test_event_callback_and_user_data_survive_collection(
    lv_screen,
    force_collection,
):
    import lvgl.mpy as lv

    calls = []
    sentinel = object()
    obj = lv.obj(lv_screen)

    def install_callback():
        def callback(event):
            calls.append(event.get_user_data())

        obj.add_event_cb(callback, lv.EVENT.CLICKED, sentinel)

    install_callback()
    junk = force_collection()
    obj.send_event(lv.EVENT.CLICKED, None)

    assert calls == [sentinel]
    assert junk


def test_remove_event_dsc_releases_callback_registration(lv_screen):
    import lvgl.mpy as lv

    obj = lv.obj(lv_screen)
    before = len(lv._global_cb_store)

    descriptor = obj.add_event_cb(
        lambda event: None,
        lv.EVENT.CLICKED,
        object(),
    )
    assert len(lv._global_cb_store) == before + 1

    assert obj.remove_event_dsc(descriptor)
    assert len(lv._global_cb_store) == before


def test_foreign_user_data_is_not_treated_as_callback_handle():
    import lvgl._raw as raw
    import lvgl.mpy as lv

    assert lv._callback_ref_from_user_data(raw.void(1)) is None


def test_remove_event_by_index_releases_callback_registration(lv_screen):
    import lvgl.mpy as lv

    obj = lv.obj(lv_screen)
    before = len(lv._global_cb_store)
    obj.add_event_cb(lambda event: None, lv.EVENT.CLICKED, object())
    assert len(lv._global_cb_store) == before + 1

    assert obj.remove_event(0)
    assert len(lv._global_cb_store) == before


def test_delete_releases_subtree_callbacks_and_retained_refs(lv_screen):
    import lvgl.mpy as lv

    parent = lv.obj(lv_screen)
    child = lv.obj(parent)
    style = lv.style_t()
    style.init()
    child.add_style(style, 0)
    child_key = lv._obj_ref_key(child)
    before = len(lv._global_cb_store)

    parent.add_event_cb(lambda event: None, lv.EVENT.CLICKED, object())
    child.add_event_cb(lambda event: None, lv.EVENT.CLICKED, object())
    assert len(lv._global_cb_store) == before + 2
    assert child_key in lv._retained_obj_refs

    parent.delete()

    assert len(lv._global_cb_store) == before
    assert child_key not in lv._retained_obj_refs
