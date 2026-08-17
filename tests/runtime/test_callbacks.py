import pytest


def _release_callback_ref(raw, pointer):
    raw._callback_object_handles.pop(id(pointer), None)


def test_callback_pointer_return_none_is_null():
    import lvgl._raw as raw

    assert (
        raw._get_callback_return(None, "void", True)
        == raw._lib_lvgl.ffi.NULL
    )


def test_callback_object_handle_round_trip_and_release():
    import lvgl._raw as raw

    ffi = raw._lib_lvgl.ffi
    value = {"file": object()}
    before = len(raw._callback_object_handles)
    pointer = raw._get_callback_return(value, "void", True)

    assert ffi.from_handle(pointer) is value
    assert len(raw._callback_object_handles) == before + 1

    raw._release_callback_object_handle(pointer)
    assert len(raw._callback_object_handles) == before


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("callback text", b"callback text"),
        (b"bytes", b"bytes"),
        (bytearray(b"bytearray"), b"bytearray"),
        (memoryview(bytearray(b"memoryview")), b"memoryview"),
    ],
    ids=["str", "bytes", "bytearray", "memoryview"],
)
def test_callback_pointer_return_retains_string_and_buffer(value, expected):
    import lvgl._raw as raw

    ffi = raw._lib_lvgl.ffi
    before = len(raw._callback_object_handles)
    pointer = raw._get_callback_return(value, "char", True)
    try:
        assert ffi.string(ffi.cast("char *", pointer), len(expected)) == expected
        assert len(raw._callback_object_handles) == before + 1
    finally:
        _release_callback_ref(raw, pointer)

    assert len(raw._callback_object_handles) == before


def test_callback_scalar_pointer_dereference_reads_and_writes():
    import lvgl._raw as raw

    pointer = raw._lib_lvgl.ffi.new("int32_t *", 12)
    wrapped = raw._get_py_callback_ptr(pointer, "int32_t")

    assert wrapped.__dereference__() == 12
    wrapped[0] = 34
    assert pointer[0] == 34

def test_scalar_callback_pointer_sized_dereference_is_writable():
    import struct
    import lvgl._raw as raw

    ffi = raw._lib_lvgl.ffi

    value = ffi.new("uint32_t *", 0)

    ptr = raw._get_py_callback_ptr(
        value,
        "uint32_t",
    )

    view = ptr.__dereference__(4)

    assert view is not None
    assert len(view) == 4

    view[0:4] = struct.pack("<L", 1234)

    assert value[0] == 1234


def test_scalar_callback_pointer_unsized_dereference_returns_value():
    import lvgl._raw as raw

    ffi = raw._lib_lvgl.ffi

    value = ffi.new("uint32_t *", 1234)

    ptr = raw._get_py_callback_ptr(
        value,
        "uint32_t",
    )

    assert ptr.__dereference__() == 1234

    ptr[0] = 5678
    assert value[0] == 5678
