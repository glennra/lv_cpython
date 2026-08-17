import pytest


pytestmark = [pytest.mark.integration, pytest.mark.sdl]


def test_sdl_display_and_window(lv):
    width, height = lv.sdl_get_display_size(0)
    assert width > 0
    assert height > 0

    display = lv.sdl_window_create(320, 240)
    try:
        assert display is not None
    finally:
        display.delete()
        lv.sdl_quit()
