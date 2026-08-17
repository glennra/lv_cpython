def test_filesystem_handle_survives_collection(
    memory_filesystem,
    force_collection,
):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    file = lv.fs_file_t()
    handles_before = len(raw._callback_object_handles)
    assert file.open("M:/hello.txt", lv.FS_MODE.RD) == lv.FS_RES.OK
    assert len(raw._callback_object_handles) == handles_before + 1

    junk = force_collection()
    output = bytearray(5)
    bytes_read = raw._lib_lvgl.ffi.new("uint32_t *")
    assert file.read(output, len(output), bytes_read) == lv.FS_RES.OK
    assert bytes_read[0] == 5
    assert output == b"hello"
    assert file.seek(6, lv.FS_SEEK.SET) == lv.FS_RES.OK
    assert file.read(output, len(output), bytes_read) == lv.FS_RES.OK
    assert output == b"world"
    assert file.close() == lv.FS_RES.OK
    assert len(raw._callback_object_handles) == handles_before
    assert junk
