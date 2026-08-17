def test_char_pointer_array():
    import lvgl._raw as raw

    ffi = raw._lib_lvgl.ffi
    array_type = type(
        "char *[]",
        (raw._Array,),
        {"_c_type": "char *"},
    )
    owner = array_type()
    owner.extend(["q", "w", "\n", "a", None])

    array = owner._obj

    assert ffi.string(array[0]) == b"q"
    assert ffi.string(array[1]) == b"w"
    assert ffi.string(array[2]) == b"\n"
    assert ffi.string(array[3]) == b"a"
    assert array[4] == ffi.NULL


def test_make_char_pointer_array():
    import lvgl._raw as raw

    ffi = raw._lib_lvgl.ffi
    owner = raw._make_c_array(
        ["q", "w", "\n", None],
        "List[char *]",
    )
    array = owner._obj

    assert ffi.string(array[0]) == b"q"
    assert ffi.string(array[1]) == b"w"
    assert ffi.string(array[2]) == b"\n"
    assert array[3] == ffi.NULL
