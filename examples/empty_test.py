try:
    import lvgl._raw as lv
except ImportError:
    import os
    import sys

    base_path = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

    import lvgl._raw as lv


# Memory use

# 953.90k of Just Python
# 1944k lvgl module loaded
# 4166k lvgl running with a blank display
# ----------------------------------------------
# 1944 - 953.90 = 990.1
# LVGL CPython library uses 990.1k of memory
#
# 4166 - 953.90 = 3212.1
# LVGL running with a blank 800 x 600 x 32bit display
# uses 3212.1k of memory
#
# 800 * 600 * 4 = 1920
# the display buffer uses 1920k
#
# 3212.1 - 1920 = 1,292.1
# the CPython binding running with a blank display consumes 1292.1k of memory
#
# 1292.1 - 990.1 = 302
# LVGL and SDL 2 are using 302 K of memory


import time


def tick_cb():
    return int(time.monotonic() * 1000)


lv.init()

lv.tick_set_cb(tick_cb)

disp = lv.sdl_window_create(430, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)

while True:
    time.sleep(0.001)
    lv.task_handler()
