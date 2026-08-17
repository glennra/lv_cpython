import struct

import pytest

import lvgl.mpy as lv
import lvgl._raw as raw


def _ensure_lvgl_initialized():
    lib = raw._lib_lvgl.lib

    if hasattr(lib, "lv_is_initialized"):
        if not lib.lv_is_initialized():
            lv.init()
    else:
        lv.init()


@pytest.fixture(scope="module")
def memory_fs():
    """Register a small in-memory filesystem on Q:."""
    _ensure_lvgl_initialized()

    files = {
        "hello.txt": b"hello world",
        "binary.bin": bytes(range(32)),
    }

    state = {
        "open_count": 0,
        "close_count": 0,
        "read_count": 0,
        "seek_count": 0,
        "tell_count": 0,
    }

    def open_cb(drv, path, mode):
        # This also tests char * callback argument conversion.
        assert isinstance(path, str)

        name = path.lstrip("/")
        data = files.get(name)

        if data is None:
            return None

        state["open_count"] += 1

        # Deliberately return an arbitrary Python object.  The binding must
        # convert this to a void * handle and recover it in later callbacks.
        return {
            "name": name,
            "data": data,
            "pos": 0,
            "closed": False,
        }

    def close_cb(drv, file_p):
        file_state = file_p.__cast__()

        assert isinstance(file_state, dict)
        assert not file_state["closed"]

        file_state["closed"] = True
        state["close_count"] += 1

        return lv.FS_RES.OK

    def read_cb(drv, file_p, buf, btr, br):
        file_state = file_p.__cast__()

        assert isinstance(file_state, dict)
        assert not file_state["closed"]
        assert isinstance(btr, int)

        start = file_state["pos"]
        end = min(start + btr, len(file_state["data"]))
        data = file_state["data"][start:end]

        if data:
            buf.__dereference__(btr)[0:len(data)] = data

        # This is intentionally identical to the MicroPythonOS operation
        # which exposed the _CallbackScalarPointer regression.
        br.__dereference__(4)[0:4] = struct.pack("<L", len(data))

        file_state["pos"] = end
        state["read_count"] += 1

        return lv.FS_RES.OK

    def seek_cb(drv, file_p, pos, whence):
        file_state = file_p.__cast__()

        if whence == lv.FS_SEEK.SET:
            new_pos = pos
        elif whence == lv.FS_SEEK.CUR:
            new_pos = file_state["pos"] + pos
        elif whence == lv.FS_SEEK.END:
            new_pos = len(file_state["data"]) + pos
        else:
            return lv.FS_RES.INV_PARAM

        if new_pos < 0:
            return lv.FS_RES.INV_PARAM

        file_state["pos"] = new_pos
        state["seek_count"] += 1

        return lv.FS_RES.OK

    def tell_cb(drv, file_p, pos_p):
        file_state = file_p.__cast__()

        pos_p.__dereference__(4)[0:4] = struct.pack(
            "<L",
            file_state["pos"],
        )

        state["tell_count"] += 1
        return lv.FS_RES.OK

    drv = lv.fs_drv_t()
    drv.init()

    drv.letter = ord("Q")
    drv.open_cb = open_cb
    drv.close_cb = close_cb
    drv.read_cb = read_cb
    drv.seek_cb = seek_cb
    drv.tell_cb = tell_cb

    drv.register()

    # Keep drv alive for the complete module.  This test is concerned with
    # file-handle lifetime rather than driver-registration lifetime.
    return drv, state


def test_filesystem_read_callback(memory_fs):
    _, state = memory_fs

    ffi = raw._lib_lvgl.ffi
    lib = raw._lib_lvgl.lib

    file_p = ffi.new("lv_fs_file_t *")

    result = lib.lv_fs_open(
        file_p,
        b"Q:/hello.txt",
        int(lv.FS_MODE.RD),
    )
    assert result == int(lv.FS_RES.OK)

    buf = ffi.new("uint8_t[5]")
    br = ffi.new("uint32_t *", 0)

    result = lib.lv_fs_read(
        file_p,
        buf,
        5,
        br,
    )

    assert result == int(lv.FS_RES.OK)
    assert br[0] == 5
    assert bytes(ffi.buffer(buf, br[0])) == b"hello"

    result = lib.lv_fs_close(file_p)

    assert result == int(lv.FS_RES.OK)
    assert state["open_count"] >= 1
    assert state["read_count"] >= 1
    assert state["close_count"] >= 1


def test_filesystem_seek_and_tell(memory_fs):
    _, _state = memory_fs

    ffi = raw._lib_lvgl.ffi
    lib = raw._lib_lvgl.lib

    file_p = ffi.new("lv_fs_file_t *")

    result = lib.lv_fs_open(
        file_p,
        b"Q:/hello.txt",
        int(lv.FS_MODE.RD),
    )
    assert result == int(lv.FS_RES.OK)

    result = lib.lv_fs_seek(
        file_p,
        6,
        int(lv.FS_SEEK.SET),
    )
    assert result == int(lv.FS_RES.OK)

    pos = ffi.new("uint32_t *", 0)

    result = lib.lv_fs_tell(
        file_p,
        pos,
    )
    assert result == int(lv.FS_RES.OK)
    assert pos[0] == 6

    buf = ffi.new("uint8_t[5]")
    br = ffi.new("uint32_t *", 0)

    result = lib.lv_fs_read(
        file_p,
        buf,
        5,
        br,
    )

    assert result == int(lv.FS_RES.OK)
    assert br[0] == 5
    assert bytes(ffi.buffer(buf, 5)) == b"world"

    assert lib.lv_fs_close(file_p) == int(lv.FS_RES.OK)


def test_filesystem_binary_read(memory_fs):
    _, _state = memory_fs

    ffi = raw._lib_lvgl.ffi
    lib = raw._lib_lvgl.lib

    file_p = ffi.new("lv_fs_file_t *")

    assert (
        lib.lv_fs_open(
            file_p,
            b"Q:/binary.bin",
            int(lv.FS_MODE.RD),
        )
        == int(lv.FS_RES.OK)
    )

    buf = ffi.new("uint8_t[32]")
    br = ffi.new("uint32_t *", 0)

    assert (
        lib.lv_fs_read(
            file_p,
            buf,
            32,
            br,
        )
        == int(lv.FS_RES.OK)
    )

    assert br[0] == 32
    assert bytes(ffi.buffer(buf, br[0])) == bytes(range(32))

    assert lib.lv_fs_close(file_p) == int(lv.FS_RES.OK)
    