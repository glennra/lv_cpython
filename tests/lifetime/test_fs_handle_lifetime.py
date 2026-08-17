import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


SCRIPT = r'''
import gc
import struct

import lvgl.mpy as lv
import lvgl._raw as raw


ffi = raw._lib_lvgl.ffi
lib = raw._lib_lvgl.lib


if hasattr(lib, "lv_is_initialized"):
    if not lib.lv_is_initialized():
        lv.init()
else:
    lv.init()


PAYLOAD = (
    b"The filesystem handle must remain valid after the Python object "
    b"returned by open_cb has gone out of local scope."
)


opened_object_id = None
close_seen = False


def open_cb(drv, path, mode):
    global opened_object_id

    assert isinstance(path, str)

    # This object has no intentional Python owner after this function
    # returns.  Its lifetime must be maintained by the binding's void *
    # handle mechanism.
    file_state = {
        "data": PAYLOAD,
        "pos": 0,
        "closed": False,
    }

    opened_object_id = id(file_state)

    return file_state


def close_cb(drv, file_p):
    global close_seen

    file_state = file_p.__cast__()

    assert id(file_state) == opened_object_id
    assert not file_state["closed"]

    file_state["closed"] = True
    close_seen = True

    return lv.FS_RES.OK


def read_cb(drv, file_p, buf, btr, br):
    file_state = file_p.__cast__()

    # Every callback must recover the exact same Python object.
    assert id(file_state) == opened_object_id
    assert not file_state["closed"]

    start = file_state["pos"]
    end = min(start + btr, len(file_state["data"]))
    data = file_state["data"][start:end]

    if data:
        buf.__dereference__(btr)[0:len(data)] = data

    br.__dereference__(4)[0:4] = struct.pack("<L", len(data))

    file_state["pos"] = end

    return lv.FS_RES.OK


def seek_cb(drv, file_p, pos, whence):
    file_state = file_p.__cast__()

    assert id(file_state) == opened_object_id

    if whence == lv.FS_SEEK.SET:
        file_state["pos"] = pos
    elif whence == lv.FS_SEEK.CUR:
        file_state["pos"] += pos
    elif whence == lv.FS_SEEK.END:
        file_state["pos"] = len(file_state["data"]) + pos
    else:
        return lv.FS_RES.INV_PARAM

    return lv.FS_RES.OK


def tell_cb(drv, file_p, pos_p):
    file_state = file_p.__cast__()

    assert id(file_state) == opened_object_id

    pos_p.__dereference__(4)[0:4] = struct.pack(
        "<L",
        file_state["pos"],
    )

    return lv.FS_RES.OK


drv = lv.fs_drv_t()
drv.init()

drv.letter = ord("Z")
drv.open_cb = open_cb
drv.close_cb = close_cb
drv.read_cb = read_cb
drv.seek_cb = seek_cb
drv.tell_cb = tell_cb

drv.register()


file_p = ffi.new("lv_fs_file_t *")

result = lib.lv_fs_open(
    file_p,
    b"Z:/lifetime.bin",
    int(lv.FS_MODE.RD),
)
assert result == int(lv.FS_RES.OK)


# open_cb's file_state local variable is now gone.
#
# Repeated collection plus allocator churn makes a dangling handle much more
# likely to fail deterministically instead of accidentally continuing to work.
for iteration in range(8):
    gc.collect()

    junk = [
        bytearray(1024 + ((i + iteration) % 257))
        for i in range(2000)
    ]

    del junk
    gc.collect()


# Read the file in several callbacks so the opaque Python handle is recovered
# repeatedly after GC and allocation churn.
received = bytearray()

while True:
    buf = ffi.new("uint8_t[11]")
    br = ffi.new("uint32_t *", 0)

    result = lib.lv_fs_read(
        file_p,
        buf,
        11,
        br,
    )

    assert result == int(lv.FS_RES.OK)

    if br[0] == 0:
        break

    received.extend(
        bytes(ffi.buffer(buf, br[0]))
    )

    gc.collect()


assert bytes(received) == PAYLOAD


# Verify that seek/tell still recover the same Python handle.
assert (
    lib.lv_fs_seek(
        file_p,
        4,
        int(lv.FS_SEEK.SET),
    )
    == int(lv.FS_RES.OK)
)

pos = ffi.new("uint32_t *", 0)

assert (
    lib.lv_fs_tell(
        file_p,
        pos,
    )
    == int(lv.FS_RES.OK)
)

assert pos[0] == 4


# More churn before close.  close_cb must still be able to recover the same
# Python state object.
for _ in range(4):
    gc.collect()
    junk = [bytearray(4096) for _ in range(500)]
    del junk


assert lib.lv_fs_close(file_p) == int(lv.FS_RES.OK)
assert close_seen
'''


def test_filesystem_python_handle_survives_gc_and_allocator_churn():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            SCRIPT,
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, (
        "filesystem lifetime subprocess failed\n\n"
        f"stdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )
    