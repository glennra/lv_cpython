def test_image_descriptor_buffer_survives_collection(force_collection):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    data = bytearray([1, 2, 3, 4])
    descriptor = lv.image_dsc_t({"data_size": len(data), "data": data})

    del data
    junk = force_collection()

    assert bytes(raw._lib_lvgl.ffi.buffer(descriptor._obj.data, 4)) == bytes(
        [1, 2, 3, 4]
    )
    assert junk


def test_replacing_image_descriptor_buffer_replaces_references():
    import lvgl.mpy as lv

    descriptor = lv.image_dsc_t()
    first = bytearray([1, 2, 3, 4])
    second = bytearray([5, 6, 7, 8])
    descriptor.data = first
    first_c_obj = descriptor.__dict__["__c_data__"]

    descriptor.data = second

    assert descriptor.__dict__["__py_data__"] is second
    assert descriptor.__dict__["__c_data__"] is not first_c_obj
