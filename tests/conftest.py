import os
from pathlib import Path
import subprocess
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The builder is repository tooling rather than an installed package. Ensure
# generator tests import the source tree regardless of pytest's import mode or
# the directory from which pytest was invoked.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_sessionstart(session):
    """Regenerate generated LVGL wrappers before collecting tests."""
    if os.environ.get("LV_SKIP_REGENERATION") == "1":
        return

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "builder.regenerate",
                "all",
            ],
            cwd=PROJECT_ROOT,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        pytest.exit(
            "LVGL wrapper regeneration failed with exit code "
            f"{exc.returncode}",
            returncode=1,
        )


@pytest.fixture
def force_collection():
    """Collect cyclic garbage and overwrite recently freed small allocations."""
    import gc

    def collect():
        for _ in range(5):
            gc.collect()

        junk = [bytearray(1024 + (index % 128)) for index in range(1000)]
        gc.collect()
        return junk

    return collect


@pytest.fixture
def lv():
    """Provide a freshly initialized LVGL binding for a single test."""
    import lvgl.mpy as lvgl

    if lvgl.is_initialized():
        lvgl.deinit()

    lvgl.init()
    try:
        yield lvgl
    finally:
        if lvgl.is_initialized():
            lvgl.deinit()


@pytest.fixture
def lv_display(lv):
    """Provide a small headless display with LVGL-managed teardown."""
    display = lv.display_create(320, 240)
    try:
        yield display
    finally:
        display.delete()


@pytest.fixture
def lv_screen(lv, lv_display):
    """Provide the active screen for the headless test display."""
    return lv.screen_active()


@pytest.fixture
def memory_filesystem(lv):
    """Register an in-memory read-only filesystem on drive M."""
    from pathlib import Path

    import lvgl._raw as raw

    root = Path(__file__).resolve().parent.parent
    files = {
        "/hello.txt": b"hello world",
        "/test.ttf": (
            root / "src/lvgl/scripts/built_in_font/unscii-8.ttf"
        ).read_bytes(),
        "/tiny.png": (
            root / "src/lvgl/examples/libs/lodepng/wink.png"
        ).read_bytes(),
    }
    driver = lv.fs_drv_t()
    driver.init()
    driver.letter = ord("M")

    def open_cb(drv, path, mode):
        return {"buffer": bytearray(files[path]), "pos": 0}

    def close_cb(drv, file):
        raw._release_callback_object_handle(file._obj)
        return lv.FS_RES.OK

    def read_cb(drv, file, buf, bytes_to_read, bytes_read):
        state = file.__cast__()
        start = state["pos"]
        data = state["buffer"][start:start + bytes_to_read]
        buf.__dereference__(len(data))[:] = data
        bytes_read[0] = len(data)
        state["pos"] += len(data)
        return lv.FS_RES.OK

    def seek_cb(drv, file, position, whence):
        state = file.__cast__()
        if whence == lv.FS_SEEK.SET:
            state["pos"] = position
        elif whence == lv.FS_SEEK.CUR:
            state["pos"] += position
        else:
            state["pos"] = len(state["buffer"]) + position
        return lv.FS_RES.OK

    def tell_cb(drv, file, position):
        position[0] = file.__cast__()["pos"]
        return lv.FS_RES.OK

    driver.open_cb = open_cb
    driver.close_cb = close_cb
    driver.read_cb = read_cb
    driver.seek_cb = seek_cb
    driver.tell_cb = tell_cb
    driver.register()

    yield driver
