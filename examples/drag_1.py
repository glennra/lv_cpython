try:
    import lvgl._raw as lv
except ImportError:
    import os
    import sys

    base_path = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

    import lvgl._raw as lv

import time

lv.init()
disp = lv.sdl_window_create(480, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


def drag_event_handler(e):
    target = lv.event_get_target_obj(e)
    indev = lv.indev_active()
    if indev is None:
        return

    vect = lv.point_t()
    lv.indev_get_vect(indev, vect)
    x = lv.obj_get_x_aligned(target) + vect.x
    y = lv.obj_get_y_aligned(target) + vect.y
    lv.obj_set_pos(target, x, y)


#
# Make an object dragable.
#

obj = lv.obj_create(lv.screen_active())
lv.obj_set_size(obj, 150, 100)
lv.obj_add_event_cb(obj, drag_event_handler, lv.EVENT_PRESSING, None)

label = lv.label_create(obj)
lv.label_set_text(label, "Drag me")
lv.obj_center(label)

start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
