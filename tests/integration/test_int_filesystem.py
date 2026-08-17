def test_filesystem_callbacks_round_trip(memory_filesystem):
    import lvgl._raw as raw
    import lvgl.mpy as lv

    file = lv.fs_file_t()
    output = bytearray(11)
    bytes_read = raw._lib_lvgl.ffi.new("uint32_t *")
    position = raw._lib_lvgl.ffi.new("uint32_t *")
    handles_before = len(raw._callback_object_handles)

    assert file.open("M:/hello.txt", lv.FS_MODE.RD) == lv.FS_RES.OK
    assert len(raw._callback_object_handles) == handles_before + 1
    assert file.read(output, len(output), bytes_read) == lv.FS_RES.OK
    assert bytes_read[0] == len(output)
    assert output == b"hello world"
    assert file.seek(6, lv.FS_SEEK.SET) == lv.FS_RES.OK
    assert file.tell(position) == lv.FS_RES.OK
    assert position[0] == 6
    assert file.close() == lv.FS_RES.OK
    assert len(raw._callback_object_handles) == handles_before
