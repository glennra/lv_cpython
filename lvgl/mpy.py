from typing import Union, Any, Callable, Optional, List  # NOQA
import importlib as _importlib

_lvgl = _importlib.import_module(__package__ + "._raw")
_MPY_API = True


_retained_obj_refs = {}

def _obj_ref_key(obj):
    ptr = _lvgl._lib_lvgl.ffi.cast("uintptr_t", obj._obj)
    return int(ptr)

def _retain_obj_ref(obj, slot, value, append=False):
    refs = _retained_obj_refs.setdefault(_obj_ref_key(obj), {})
    if append:
        values = refs.setdefault(slot, [])
        if not any(item is value for item in values):
            values.append(value)
    else:
        refs[slot] = value

def _release_obj_refs(obj, slot=None):
    key = _obj_ref_key(obj)
    if slot is None:
        _retained_obj_refs.pop(key, None)
        return
    refs = _retained_obj_refs.get(key)
    if refs is None:
        return
    refs.pop(slot, None)
    if not refs:
        _retained_obj_refs.pop(key, None)

def _callback_ref_from_user_data(user_data):
    if user_data is None or not hasattr(user_data, "_obj"):
        return None
    ffi = _lvgl._lib_lvgl.ffi
    pointer = int(ffi.cast("uintptr_t", user_data._obj))
    for ref, store in _lvgl._global_cb_store.items():
        if not isinstance(store, _lvgl._CBStore):
            continue
        handle = store.get("__handle__")
        if handle is None:
            continue
        if int(ffi.cast("uintptr_t", handle)) == pointer:
            return ref
    return None

def _event_callback_ref(dsc):
    return _callback_ref_from_user_data(
        _lvgl.event_dsc_get_user_data(dsc)
    )

def _release_event_callback_ref(ref):
    if ref is not None:
        _lvgl._global_cb_store.pop(ref, None)

def _collect_obj_release_refs(obj):
    refs = [(_obj_ref_key(obj), [])]
    event_refs = refs[0][1]
    for index in range(_lvgl.obj_get_event_count(obj)):
        dsc = _lvgl.obj_get_event_dsc(obj, index)
        event_refs.append(_event_callback_ref(dsc))
    for index in range(_lvgl.obj_get_child_count(obj)):
        child = _lvgl.obj_get_child(obj, index)
        refs.extend(_collect_obj_release_refs(child))
    return refs

def _release_collected_obj_refs(refs):
    for obj_key, event_refs in refs:
        _retained_obj_refs.pop(obj_key, None)
        for ref in event_refs:
            _release_event_callback_ref(ref)


class SYMBOL:
    BULLET = '•'
    AUDIO = '\uf001'
    VIDEO = '\uf008'
    LIST = '\uf00b'
    OK = '\uf00c'
    CLOSE = '\uf00d'
    POWER = '\uf011'
    SETTINGS = '\uf013'
    HOME = '\uf015'
    DOWNLOAD = '\uf019'
    DRIVE = '\uf01c'
    REFRESH = '\uf021'
    MUTE = '\uf026'
    VOLUME_MID = '\uf027'
    VOLUME_MAX = '\uf028'
    IMAGE = '\uf03e'
    TINT = '\uf043'
    PREV = '\uf048'
    PLAY = '\uf04b'
    PAUSE = '\uf04c'
    STOP = '\uf04d'
    NEXT = '\uf051'
    EJECT = '\uf052'
    LEFT = '\uf053'
    RIGHT = '\uf054'
    PLUS = '\uf067'
    MINUS = '\uf068'
    EYE_OPEN = '\uf06e'
    EYE_CLOSE = '\uf070'
    WARNING = '\uf071'
    SHUFFLE = '\uf074'
    UP = '\uf077'
    DOWN = '\uf078'
    LOOP = '\uf079'
    DIRECTORY = '\uf07b'
    UPLOAD = '\uf093'
    CALL = '\uf095'
    CUT = '\uf0c4'
    COPY = '\uf0c5'
    SAVE = '\uf0c7'
    BARS = '\uf0c9'
    ENVELOPE = '\uf0e0'
    CHARGE = '\uf0e7'
    PASTE = '\uf0ea'
    BELL = '\uf0f3'
    KEYBOARD = '\uf11c'
    GPS = '\uf124'
    FILE = '\uf15b'
    WIFI = '\uf1eb'
    BATTERY_FULL = '\uf240'
    BATTERY_3 = '\uf241'
    BATTERY_2 = '\uf242'
    BATTERY_1 = '\uf243'
    BATTERY_EMPTY = '\uf244'
    USB = '\uf287'
    BLUETOOTH = '\uf293'
    TRASH = '\uf2ed'
    EDIT = '\uf304'
    BACKSPACE = '\uf55a'
    SD_CARD = '\uf7c2'
    NEW_LINE = '\uf8a2'
    DUMMY = '\uf8ff'


RADIUS_CIRCLE = _lvgl.RADIUS_CIRCLE

IMAGE_HEADER_MAGIC = _lvgl.IMAGE_HEADER_MAGIC

GRID_CONTENT = _lvgl.GRID_CONTENT

GRID_TEMPLATE_LAST = _lvgl.GRID_TEMPLATE_LAST


class EXPLORER:
    SORT_NONE = _lvgl.EXPLORER_SORT_NONE
    SORT_KIND = _lvgl.EXPLORER_SORT_KIND
    HOME_DIR = _lvgl.EXPLORER_HOME_DIR
    MUSIC_DIR = _lvgl.EXPLORER_MUSIC_DIR
    PICTURES_DIR = _lvgl.EXPLORER_PICTURES_DIR
    VIDEO_DIR = _lvgl.EXPLORER_VIDEO_DIR
    DOCS_DIR = _lvgl.EXPLORER_DOCS_DIR
    FS_DIR = _lvgl.EXPLORER_FS_DIR


class INDEV_TYPE:
    NONE = _lvgl.INDEV_TYPE_NONE
    POINTER = _lvgl.INDEV_TYPE_POINTER
    KEYPAD = _lvgl.INDEV_TYPE_KEYPAD
    BUTTON = _lvgl.INDEV_TYPE_BUTTON
    ENCODER = _lvgl.INDEV_TYPE_ENCODER


class INDEV_STATE:
    RELEASED = _lvgl.INDEV_STATE_RELEASED
    PRESSED = _lvgl.INDEV_STATE_PRESSED


class DRAW_MASK:
    pass


class DRAW_LAYER:
    pass


class FS_RES:
    OK = _lvgl.FS_RES_OK
    HW_ERR = _lvgl.FS_RES_HW_ERR
    FS_ERR = _lvgl.FS_RES_FS_ERR
    NOT_EX = _lvgl.FS_RES_NOT_EX
    FULL = _lvgl.FS_RES_FULL
    LOCKED = _lvgl.FS_RES_LOCKED
    DENIED = _lvgl.FS_RES_DENIED
    BUSY = _lvgl.FS_RES_BUSY
    TOUT = _lvgl.FS_RES_TOUT
    NOT_IMP = _lvgl.FS_RES_NOT_IMP
    OUT_OF_MEM = _lvgl.FS_RES_OUT_OF_MEM
    INV_PARAM = _lvgl.FS_RES_INV_PARAM
    DRIVE_LETTER_ALREADY_USED = _lvgl.FS_RES_DRIVE_LETTER_ALREADY_USED
    UNKNOWN = _lvgl.FS_RES_UNKNOWN


class FS_MODE:
    WR = _lvgl.FS_MODE_WR
    RD = _lvgl.FS_MODE_RD


class FS_SEEK:
    SET = _lvgl.FS_SEEK_SET
    CUR = _lvgl.FS_SEEK_CUR
    END = _lvgl.FS_SEEK_END


class DISP_ROTATION:
    pass


class FONT_SUBPX:
    NONE = _lvgl.FONT_SUBPX_NONE
    HOR = _lvgl.FONT_SUBPX_HOR
    VER = _lvgl.FONT_SUBPX_VER
    BOTH = _lvgl.FONT_SUBPX_BOTH


class ANIM_IMG:
    pass


class SPAN_MODE:
    FIXED = _lvgl.SPAN_MODE_FIXED
    EXPAND = _lvgl.SPAN_MODE_EXPAND
    BREAK = _lvgl.SPAN_MODE_BREAK
    LAST = _lvgl.SPAN_MODE_LAST


class SPAN_OVERFLOW:
    CLIP = _lvgl.SPAN_OVERFLOW_CLIP
    ELLIPSIS = _lvgl.SPAN_OVERFLOW_ELLIPSIS
    LAST = _lvgl.SPAN_OVERFLOW_LAST


class FLEX_ALIGN:
    START = _lvgl.FLEX_ALIGN_START
    END = _lvgl.FLEX_ALIGN_END
    CENTER = _lvgl.FLEX_ALIGN_CENTER
    SPACE_EVENLY = _lvgl.FLEX_ALIGN_SPACE_EVENLY
    SPACE_AROUND = _lvgl.FLEX_ALIGN_SPACE_AROUND
    SPACE_BETWEEN = _lvgl.FLEX_ALIGN_SPACE_BETWEEN


class FLEX_FLOW:
    ROW = _lvgl.FLEX_FLOW_ROW
    COLUMN = _lvgl.FLEX_FLOW_COLUMN
    ROW_WRAP = _lvgl.FLEX_FLOW_ROW_WRAP
    ROW_REVERSE = _lvgl.FLEX_FLOW_ROW_REVERSE
    ROW_WRAP_REVERSE = _lvgl.FLEX_FLOW_ROW_WRAP_REVERSE
    COLUMN_WRAP = _lvgl.FLEX_FLOW_COLUMN_WRAP
    COLUMN_REVERSE = _lvgl.FLEX_FLOW_COLUMN_REVERSE
    COLUMN_WRAP_REVERSE = _lvgl.FLEX_FLOW_COLUMN_WRAP_REVERSE


class GRID_ALIGN:
    START = _lvgl.GRID_ALIGN_START
    CENTER = _lvgl.GRID_ALIGN_CENTER
    END = _lvgl.GRID_ALIGN_END
    STRETCH = _lvgl.GRID_ALIGN_STRETCH
    SPACE_EVENLY = _lvgl.GRID_ALIGN_SPACE_EVENLY
    SPACE_AROUND = _lvgl.GRID_ALIGN_SPACE_AROUND
    SPACE_BETWEEN = _lvgl.GRID_ALIGN_SPACE_BETWEEN


class GRID:
    CONTENT = _lvgl.GRID_CONTENT
    TEMPLATE_LAST = _lvgl.GRID_TEMPLATE_LAST


class COLOR_FORMAT:
    UNKNOWN = _lvgl.COLOR_FORMAT_UNKNOWN
    RAW = _lvgl.COLOR_FORMAT_RAW
    RAW_ALPHA = _lvgl.COLOR_FORMAT_RAW_ALPHA
    L8 = _lvgl.COLOR_FORMAT_L8
    I1 = _lvgl.COLOR_FORMAT_I1
    I2 = _lvgl.COLOR_FORMAT_I2
    I4 = _lvgl.COLOR_FORMAT_I4
    I8 = _lvgl.COLOR_FORMAT_I8
    A8 = _lvgl.COLOR_FORMAT_A8
    RGB565 = _lvgl.COLOR_FORMAT_RGB565
    ARGB8565 = _lvgl.COLOR_FORMAT_ARGB8565
    RGB565A8 = _lvgl.COLOR_FORMAT_RGB565A8
    AL88 = _lvgl.COLOR_FORMAT_AL88
    RGB565_SWAPPED = _lvgl.COLOR_FORMAT_RGB565_SWAPPED
    RGB888 = _lvgl.COLOR_FORMAT_RGB888
    ARGB8888 = _lvgl.COLOR_FORMAT_ARGB8888
    XRGB8888 = _lvgl.COLOR_FORMAT_XRGB8888
    ARGB8888_PREMULTIPLIED = _lvgl.COLOR_FORMAT_ARGB8888_PREMULTIPLIED
    A1 = _lvgl.COLOR_FORMAT_A1
    A2 = _lvgl.COLOR_FORMAT_A2
    A4 = _lvgl.COLOR_FORMAT_A4
    ARGB1555 = _lvgl.COLOR_FORMAT_ARGB1555
    ARGB4444 = _lvgl.COLOR_FORMAT_ARGB4444
    ARGB2222 = _lvgl.COLOR_FORMAT_ARGB2222
    YUV_START = _lvgl.COLOR_FORMAT_YUV_START
    I420 = _lvgl.COLOR_FORMAT_I420
    I422 = _lvgl.COLOR_FORMAT_I422
    I444 = _lvgl.COLOR_FORMAT_I444
    I400 = _lvgl.COLOR_FORMAT_I400
    NV21 = _lvgl.COLOR_FORMAT_NV21
    NV12 = _lvgl.COLOR_FORMAT_NV12
    YUY2 = _lvgl.COLOR_FORMAT_YUY2
    UYVY = _lvgl.COLOR_FORMAT_UYVY
    YUV_END = _lvgl.COLOR_FORMAT_YUV_END
    PROPRIETARY_START = _lvgl.COLOR_FORMAT_PROPRIETARY_START
    NEMA_TSC_START = _lvgl.COLOR_FORMAT_NEMA_TSC_START
    NEMA_TSC4 = _lvgl.COLOR_FORMAT_NEMA_TSC4
    NEMA_TSC6 = _lvgl.COLOR_FORMAT_NEMA_TSC6
    NEMA_TSC6A = _lvgl.COLOR_FORMAT_NEMA_TSC6A
    NEMA_TSC6AP = _lvgl.COLOR_FORMAT_NEMA_TSC6AP
    NEMA_TSC12 = _lvgl.COLOR_FORMAT_NEMA_TSC12
    NEMA_TSC12A = _lvgl.COLOR_FORMAT_NEMA_TSC12A
    NEMA_TSC_END = _lvgl.COLOR_FORMAT_NEMA_TSC_END
    NATIVE = _lvgl.COLOR_FORMAT_NATIVE
    NATIVE_WITH_ALPHA = _lvgl.COLOR_FORMAT_NATIVE_WITH_ALPHA


class STYLE_RES:
    NOT_FOUND = _lvgl.STYLE_RES_NOT_FOUND
    FOUND = _lvgl.STYLE_RES_FOUND


class STYLE_PROP:
    INV = _lvgl.STYLE_PROP_INV
    ANY = _lvgl.STYLE_PROP_ANY
    CONST = _lvgl.STYLE_PROP_CONST


class SCREEN_LOAD_ANIM:
    NONE = _lvgl.SCREEN_LOAD_ANIM_NONE
    OVER_LEFT = _lvgl.SCREEN_LOAD_ANIM_OVER_LEFT
    OVER_RIGHT = _lvgl.SCREEN_LOAD_ANIM_OVER_RIGHT
    OVER_TOP = _lvgl.SCREEN_LOAD_ANIM_OVER_TOP
    OVER_BOTTOM = _lvgl.SCREEN_LOAD_ANIM_OVER_BOTTOM
    MOVE_LEFT = _lvgl.SCREEN_LOAD_ANIM_MOVE_LEFT
    MOVE_RIGHT = _lvgl.SCREEN_LOAD_ANIM_MOVE_RIGHT
    MOVE_TOP = _lvgl.SCREEN_LOAD_ANIM_MOVE_TOP
    MOVE_BOTTOM = _lvgl.SCREEN_LOAD_ANIM_MOVE_BOTTOM
    FADE_IN = _lvgl.SCREEN_LOAD_ANIM_FADE_IN
    FADE_ON = _lvgl.SCREEN_LOAD_ANIM_FADE_ON
    FADE_OUT = _lvgl.SCREEN_LOAD_ANIM_FADE_OUT
    OUT_LEFT = _lvgl.SCREEN_LOAD_ANIM_OUT_LEFT
    OUT_RIGHT = _lvgl.SCREEN_LOAD_ANIM_OUT_RIGHT
    OUT_TOP = _lvgl.SCREEN_LOAD_ANIM_OUT_TOP
    OUT_BOTTOM = _lvgl.SCREEN_LOAD_ANIM_OUT_BOTTOM


class TEXT_ALIGN:
    AUTO = _lvgl.TEXT_ALIGN_AUTO
    LEFT = _lvgl.TEXT_ALIGN_LEFT
    CENTER = _lvgl.TEXT_ALIGN_CENTER
    RIGHT = _lvgl.TEXT_ALIGN_RIGHT

DPI_DEF = _lvgl.DPI_DEF


class RESULT:
    INVALID = _lvgl.RESULT_INVALID
    OK = _lvgl.RESULT_OK


class LOG_LEVEL:
    TRACE = _lvgl.LOG_LEVEL_TRACE
    INFO = _lvgl.LOG_LEVEL_INFO
    WARN = _lvgl.LOG_LEVEL_WARN
    ERROR = _lvgl.LOG_LEVEL_ERROR
    USER = _lvgl.LOG_LEVEL_USER
    NONE = _lvgl.LOG_LEVEL_NONE


class ANIM:
    REPEAT_INFINITE = _lvgl.ANIM_REPEAT_INFINITE
    PLAYTIME_INFINITE = _lvgl.ANIM_PLAYTIME_INFINITE
    IMAGE_PART_MAIN = _lvgl.ANIM_IMAGE_PART_MAIN


class RB_COLOR:
    RED = _lvgl.RB_COLOR_RED
    BLACK = _lvgl.RB_COLOR_BLACK


class ALIGN:
    DEFAULT = _lvgl.ALIGN_DEFAULT
    TOP_LEFT = _lvgl.ALIGN_TOP_LEFT
    TOP_MID = _lvgl.ALIGN_TOP_MID
    TOP_RIGHT = _lvgl.ALIGN_TOP_RIGHT
    BOTTOM_LEFT = _lvgl.ALIGN_BOTTOM_LEFT
    BOTTOM_MID = _lvgl.ALIGN_BOTTOM_MID
    BOTTOM_RIGHT = _lvgl.ALIGN_BOTTOM_RIGHT
    LEFT_MID = _lvgl.ALIGN_LEFT_MID
    RIGHT_MID = _lvgl.ALIGN_RIGHT_MID
    CENTER = _lvgl.ALIGN_CENTER
    OUT_TOP_LEFT = _lvgl.ALIGN_OUT_TOP_LEFT
    OUT_TOP_MID = _lvgl.ALIGN_OUT_TOP_MID
    OUT_TOP_RIGHT = _lvgl.ALIGN_OUT_TOP_RIGHT
    OUT_BOTTOM_LEFT = _lvgl.ALIGN_OUT_BOTTOM_LEFT
    OUT_BOTTOM_MID = _lvgl.ALIGN_OUT_BOTTOM_MID
    OUT_BOTTOM_RIGHT = _lvgl.ALIGN_OUT_BOTTOM_RIGHT
    OUT_LEFT_TOP = _lvgl.ALIGN_OUT_LEFT_TOP
    OUT_LEFT_MID = _lvgl.ALIGN_OUT_LEFT_MID
    OUT_LEFT_BOTTOM = _lvgl.ALIGN_OUT_LEFT_BOTTOM
    OUT_RIGHT_TOP = _lvgl.ALIGN_OUT_RIGHT_TOP
    OUT_RIGHT_MID = _lvgl.ALIGN_OUT_RIGHT_MID
    OUT_RIGHT_BOTTOM = _lvgl.ALIGN_OUT_RIGHT_BOTTOM


class DIR:
    NONE = _lvgl.DIR_NONE
    LEFT = _lvgl.DIR_LEFT
    RIGHT = _lvgl.DIR_RIGHT
    TOP = _lvgl.DIR_TOP
    BOTTOM = _lvgl.DIR_BOTTOM
    HOR = _lvgl.DIR_HOR
    VER = _lvgl.DIR_VER
    ALL = _lvgl.DIR_ALL


class COORD:
    MAX = _lvgl.COORD_MAX
    MIN = _lvgl.COORD_MIN

SIZE_CONTENT = _lvgl.SIZE_CONTENT

COLOR_DEPTH = _lvgl.COLOR_DEPTH


class OPA:
    TRANSP = _lvgl.OPA_TRANSP
    _0 = _lvgl.OPA_0
    _10 = _lvgl.OPA_10
    _20 = _lvgl.OPA_20
    _30 = _lvgl.OPA_30
    _40 = _lvgl.OPA_40
    _50 = _lvgl.OPA_50
    _60 = _lvgl.OPA_60
    _70 = _lvgl.OPA_70
    _80 = _lvgl.OPA_80
    _90 = _lvgl.OPA_90
    _100 = _lvgl.OPA_100
    COVER = _lvgl.OPA_COVER


class PALETTE:
    RED = _lvgl.PALETTE_RED
    PINK = _lvgl.PALETTE_PINK
    PURPLE = _lvgl.PALETTE_PURPLE
    DEEP_PURPLE = _lvgl.PALETTE_DEEP_PURPLE
    INDIGO = _lvgl.PALETTE_INDIGO
    BLUE = _lvgl.PALETTE_BLUE
    LIGHT_BLUE = _lvgl.PALETTE_LIGHT_BLUE
    CYAN = _lvgl.PALETTE_CYAN
    TEAL = _lvgl.PALETTE_TEAL
    GREEN = _lvgl.PALETTE_GREEN
    LIGHT_GREEN = _lvgl.PALETTE_LIGHT_GREEN
    LIME = _lvgl.PALETTE_LIME
    YELLOW = _lvgl.PALETTE_YELLOW
    AMBER = _lvgl.PALETTE_AMBER
    ORANGE = _lvgl.PALETTE_ORANGE
    DEEP_ORANGE = _lvgl.PALETTE_DEEP_ORANGE
    BROWN = _lvgl.PALETTE_BROWN
    BLUE_GREY = _lvgl.PALETTE_BLUE_GREY
    GREY = _lvgl.PALETTE_GREY
    LAST = _lvgl.PALETTE_LAST
    NONE = _lvgl.PALETTE_NONE

STRIDE_AUTO = _lvgl.STRIDE_AUTO


class TREE_WALK:
    PRE_ORDER = _lvgl.TREE_WALK_PRE_ORDER
    POST_ORDER = _lvgl.TREE_WALK_POST_ORDER


class STR_SYMBOL:
    BULLET = _lvgl.STR_SYMBOL_BULLET
    AUDIO = _lvgl.STR_SYMBOL_AUDIO
    VIDEO = _lvgl.STR_SYMBOL_VIDEO
    LIST = _lvgl.STR_SYMBOL_LIST
    OK = _lvgl.STR_SYMBOL_OK
    CLOSE = _lvgl.STR_SYMBOL_CLOSE
    POWER = _lvgl.STR_SYMBOL_POWER
    SETTINGS = _lvgl.STR_SYMBOL_SETTINGS
    HOME = _lvgl.STR_SYMBOL_HOME
    DOWNLOAD = _lvgl.STR_SYMBOL_DOWNLOAD
    DRIVE = _lvgl.STR_SYMBOL_DRIVE
    REFRESH = _lvgl.STR_SYMBOL_REFRESH
    MUTE = _lvgl.STR_SYMBOL_MUTE
    VOLUME_MID = _lvgl.STR_SYMBOL_VOLUME_MID
    VOLUME_MAX = _lvgl.STR_SYMBOL_VOLUME_MAX
    IMAGE = _lvgl.STR_SYMBOL_IMAGE
    TINT = _lvgl.STR_SYMBOL_TINT
    PREV = _lvgl.STR_SYMBOL_PREV
    PLAY = _lvgl.STR_SYMBOL_PLAY
    PAUSE = _lvgl.STR_SYMBOL_PAUSE
    STOP = _lvgl.STR_SYMBOL_STOP
    NEXT = _lvgl.STR_SYMBOL_NEXT
    EJECT = _lvgl.STR_SYMBOL_EJECT
    LEFT = _lvgl.STR_SYMBOL_LEFT
    RIGHT = _lvgl.STR_SYMBOL_RIGHT
    PLUS = _lvgl.STR_SYMBOL_PLUS
    MINUS = _lvgl.STR_SYMBOL_MINUS
    EYE_OPEN = _lvgl.STR_SYMBOL_EYE_OPEN
    EYE_CLOSE = _lvgl.STR_SYMBOL_EYE_CLOSE
    WARNING = _lvgl.STR_SYMBOL_WARNING
    SHUFFLE = _lvgl.STR_SYMBOL_SHUFFLE
    UP = _lvgl.STR_SYMBOL_UP
    DOWN = _lvgl.STR_SYMBOL_DOWN
    LOOP = _lvgl.STR_SYMBOL_LOOP
    DIRECTORY = _lvgl.STR_SYMBOL_DIRECTORY
    UPLOAD = _lvgl.STR_SYMBOL_UPLOAD
    CALL = _lvgl.STR_SYMBOL_CALL
    CUT = _lvgl.STR_SYMBOL_CUT
    COPY = _lvgl.STR_SYMBOL_COPY
    SAVE = _lvgl.STR_SYMBOL_SAVE
    BARS = _lvgl.STR_SYMBOL_BARS
    ENVELOPE = _lvgl.STR_SYMBOL_ENVELOPE
    CHARGE = _lvgl.STR_SYMBOL_CHARGE
    PASTE = _lvgl.STR_SYMBOL_PASTE
    BELL = _lvgl.STR_SYMBOL_BELL
    KEYBOARD = _lvgl.STR_SYMBOL_KEYBOARD
    GPS = _lvgl.STR_SYMBOL_GPS
    FILE = _lvgl.STR_SYMBOL_FILE
    WIFI = _lvgl.STR_SYMBOL_WIFI
    BATTERY_FULL = _lvgl.STR_SYMBOL_BATTERY_FULL
    BATTERY_3 = _lvgl.STR_SYMBOL_BATTERY_3
    BATTERY_2 = _lvgl.STR_SYMBOL_BATTERY_2
    BATTERY_1 = _lvgl.STR_SYMBOL_BATTERY_1
    BATTERY_EMPTY = _lvgl.STR_SYMBOL_BATTERY_EMPTY
    USB = _lvgl.STR_SYMBOL_USB
    BLUETOOTH = _lvgl.STR_SYMBOL_BLUETOOTH
    TRASH = _lvgl.STR_SYMBOL_TRASH
    EDIT = _lvgl.STR_SYMBOL_EDIT
    BACKSPACE = _lvgl.STR_SYMBOL_BACKSPACE
    SD_CARD = _lvgl.STR_SYMBOL_SD_CARD
    NEW_LINE = _lvgl.STR_SYMBOL_NEW_LINE
    DUMMY = _lvgl.STR_SYMBOL_DUMMY


class FONT_GLYPH:
    FORMAT_NONE = _lvgl.FONT_GLYPH_FORMAT_NONE
    FORMAT_A1 = _lvgl.FONT_GLYPH_FORMAT_A1
    FORMAT_A2 = _lvgl.FONT_GLYPH_FORMAT_A2
    FORMAT_A3 = _lvgl.FONT_GLYPH_FORMAT_A3
    FORMAT_A4 = _lvgl.FONT_GLYPH_FORMAT_A4
    FORMAT_A8 = _lvgl.FONT_GLYPH_FORMAT_A8
    FORMAT_IMAGE = _lvgl.FONT_GLYPH_FORMAT_IMAGE
    FORMAT_VECTOR = _lvgl.FONT_GLYPH_FORMAT_VECTOR
    FORMAT_SVG = _lvgl.FONT_GLYPH_FORMAT_SVG
    FORMAT_CUSTOM = _lvgl.FONT_GLYPH_FORMAT_CUSTOM
    KERNING_NORMAL = _lvgl.FONT_KERNING_NORMAL
    KERNING_NONE = _lvgl.FONT_KERNING_NONE
    FMT_TXT_CMAP_FORMAT0_FULL = _lvgl.FONT_FMT_TXT_CMAP_FORMAT0_FULL
    FMT_TXT_CMAP_SPARSE_FULL = _lvgl.FONT_FMT_TXT_CMAP_SPARSE_FULL
    FMT_TXT_CMAP_FORMAT0_TINY = _lvgl.FONT_FMT_TXT_CMAP_FORMAT0_TINY
    FMT_TXT_CMAP_SPARSE_TINY = _lvgl.FONT_FMT_TXT_CMAP_SPARSE_TINY
    FMT_TXT_PLAIN = _lvgl.FONT_FMT_TXT_PLAIN
    FMT_TXT_COMPRESSED = _lvgl.FONT_FMT_TXT_COMPRESSED
    FMT_TXT_COMPRESSED_NO_PREFILTER = _lvgl.FONT_FMT_TXT_COMPRESSED_NO_PREFILTER


class TEXT_FLAG:
    NONE = _lvgl.TEXT_FLAG_NONE
    EXPAND = _lvgl.TEXT_FLAG_EXPAND
    FIT = _lvgl.TEXT_FLAG_FIT
    BREAK_ALL = _lvgl.TEXT_FLAG_BREAK_ALL
    RECOLOR = _lvgl.TEXT_FLAG_RECOLOR
    DECOR_NONE = _lvgl.TEXT_DECOR_NONE
    DECOR_UNDERLINE = _lvgl.TEXT_DECOR_UNDERLINE
    DECOR_STRIKETHROUGH = _lvgl.TEXT_DECOR_STRIKETHROUGH


class BASE_DIR:
    LTR = _lvgl.BASE_DIR_LTR
    RTL = _lvgl.BASE_DIR_RTL
    AUTO = _lvgl.BASE_DIR_AUTO
    NEUTRAL = _lvgl.BASE_DIR_NEUTRAL
    WEAK = _lvgl.BASE_DIR_WEAK


class GRAD_DIR:
    NONE = _lvgl.GRAD_DIR_NONE
    VER = _lvgl.GRAD_DIR_VER
    HOR = _lvgl.GRAD_DIR_HOR
    LINEAR = _lvgl.GRAD_DIR_LINEAR
    RADIAL = _lvgl.GRAD_DIR_RADIAL
    CONICAL = _lvgl.GRAD_DIR_CONICAL
    EXTEND_PAD = _lvgl.GRAD_EXTEND_PAD
    EXTEND_REPEAT = _lvgl.GRAD_EXTEND_REPEAT
    EXTEND_REFLECT = _lvgl.GRAD_EXTEND_REFLECT


class LAYOUT:
    NONE = _lvgl.LAYOUT_NONE
    FLEX = _lvgl.LAYOUT_FLEX
    GRID = _lvgl.LAYOUT_GRID
    LAST = _lvgl.LAYOUT_LAST


class BLEND_MODE:
    NORMAL = _lvgl.BLEND_MODE_NORMAL
    ADDITIVE = _lvgl.BLEND_MODE_ADDITIVE
    SUBTRACTIVE = _lvgl.BLEND_MODE_SUBTRACTIVE
    MULTIPLY = _lvgl.BLEND_MODE_MULTIPLY
    DIFFERENCE = _lvgl.BLEND_MODE_DIFFERENCE


class BORDER_SIDE:
    NONE = _lvgl.BORDER_SIDE_NONE
    BOTTOM = _lvgl.BORDER_SIDE_BOTTOM
    TOP = _lvgl.BORDER_SIDE_TOP
    LEFT = _lvgl.BORDER_SIDE_LEFT
    RIGHT = _lvgl.BORDER_SIDE_RIGHT
    FULL = _lvgl.BORDER_SIDE_FULL
    INTERNAL = _lvgl.BORDER_SIDE_INTERNAL


class BLUR_QUALITY:
    AUTO = _lvgl.BLUR_QUALITY_AUTO
    SPEED = _lvgl.BLUR_QUALITY_SPEED
    PRECISION = _lvgl.BLUR_QUALITY_PRECISION


class STYLE:
    WIDTH = _lvgl.STYLE_WIDTH
    HEIGHT = _lvgl.STYLE_HEIGHT
    LENGTH = _lvgl.STYLE_LENGTH
    TRANSFORM_WIDTH = _lvgl.STYLE_TRANSFORM_WIDTH
    TRANSFORM_HEIGHT = _lvgl.STYLE_TRANSFORM_HEIGHT
    MIN_WIDTH = _lvgl.STYLE_MIN_WIDTH
    MAX_WIDTH = _lvgl.STYLE_MAX_WIDTH
    MIN_HEIGHT = _lvgl.STYLE_MIN_HEIGHT
    MAX_HEIGHT = _lvgl.STYLE_MAX_HEIGHT
    TRANSLATE_X = _lvgl.STYLE_TRANSLATE_X
    TRANSLATE_Y = _lvgl.STYLE_TRANSLATE_Y
    RADIAL_OFFSET = _lvgl.STYLE_RADIAL_OFFSET
    X = _lvgl.STYLE_X
    Y = _lvgl.STYLE_Y
    ALIGN = _lvgl.STYLE_ALIGN
    PAD_TOP = _lvgl.STYLE_PAD_TOP
    PAD_BOTTOM = _lvgl.STYLE_PAD_BOTTOM
    PAD_LEFT = _lvgl.STYLE_PAD_LEFT
    PAD_RIGHT = _lvgl.STYLE_PAD_RIGHT
    PAD_RADIAL = _lvgl.STYLE_PAD_RADIAL
    PAD_ROW = _lvgl.STYLE_PAD_ROW
    PAD_COLUMN = _lvgl.STYLE_PAD_COLUMN
    MARGIN_TOP = _lvgl.STYLE_MARGIN_TOP
    MARGIN_BOTTOM = _lvgl.STYLE_MARGIN_BOTTOM
    MARGIN_LEFT = _lvgl.STYLE_MARGIN_LEFT
    MARGIN_RIGHT = _lvgl.STYLE_MARGIN_RIGHT
    BG_GRAD = _lvgl.STYLE_BG_GRAD
    BG_GRAD_DIR = _lvgl.STYLE_BG_GRAD_DIR
    BG_MAIN_OPA = _lvgl.STYLE_BG_MAIN_OPA
    BG_GRAD_OPA = _lvgl.STYLE_BG_GRAD_OPA
    BG_GRAD_COLOR = _lvgl.STYLE_BG_GRAD_COLOR
    BG_MAIN_STOP = _lvgl.STYLE_BG_MAIN_STOP
    BG_GRAD_STOP = _lvgl.STYLE_BG_GRAD_STOP
    BG_IMAGE_SRC = _lvgl.STYLE_BG_IMAGE_SRC
    BG_IMAGE_OPA = _lvgl.STYLE_BG_IMAGE_OPA
    BG_IMAGE_RECOLOR_OPA = _lvgl.STYLE_BG_IMAGE_RECOLOR_OPA
    BG_IMAGE_TILED = _lvgl.STYLE_BG_IMAGE_TILED
    BG_IMAGE_RECOLOR = _lvgl.STYLE_BG_IMAGE_RECOLOR
    BORDER_WIDTH = _lvgl.STYLE_BORDER_WIDTH
    BORDER_COLOR = _lvgl.STYLE_BORDER_COLOR
    BORDER_OPA = _lvgl.STYLE_BORDER_OPA
    BORDER_POST = _lvgl.STYLE_BORDER_POST
    BORDER_SIDE = _lvgl.STYLE_BORDER_SIDE
    OUTLINE_WIDTH = _lvgl.STYLE_OUTLINE_WIDTH
    OUTLINE_COLOR = _lvgl.STYLE_OUTLINE_COLOR
    OUTLINE_OPA = _lvgl.STYLE_OUTLINE_OPA
    OUTLINE_PAD = _lvgl.STYLE_OUTLINE_PAD
    BG_OPA = _lvgl.STYLE_BG_OPA
    BG_COLOR = _lvgl.STYLE_BG_COLOR
    SHADOW_WIDTH = _lvgl.STYLE_SHADOW_WIDTH
    LINE_WIDTH = _lvgl.STYLE_LINE_WIDTH
    ARC_WIDTH = _lvgl.STYLE_ARC_WIDTH
    TEXT_FONT = _lvgl.STYLE_TEXT_FONT
    IMAGE_RECOLOR_OPA = _lvgl.STYLE_IMAGE_RECOLOR_OPA
    IMAGE_OPA = _lvgl.STYLE_IMAGE_OPA
    SHADOW_OPA = _lvgl.STYLE_SHADOW_OPA
    LINE_OPA = _lvgl.STYLE_LINE_OPA
    ARC_OPA = _lvgl.STYLE_ARC_OPA
    TEXT_OPA = _lvgl.STYLE_TEXT_OPA
    SHADOW_COLOR = _lvgl.STYLE_SHADOW_COLOR
    IMAGE_RECOLOR = _lvgl.STYLE_IMAGE_RECOLOR
    LINE_COLOR = _lvgl.STYLE_LINE_COLOR
    ARC_COLOR = _lvgl.STYLE_ARC_COLOR
    TEXT_COLOR = _lvgl.STYLE_TEXT_COLOR
    ARC_IMAGE_SRC = _lvgl.STYLE_ARC_IMAGE_SRC
    SHADOW_OFFSET_X = _lvgl.STYLE_SHADOW_OFFSET_X
    SHADOW_OFFSET_Y = _lvgl.STYLE_SHADOW_OFFSET_Y
    SHADOW_SPREAD = _lvgl.STYLE_SHADOW_SPREAD
    LINE_DASH_WIDTH = _lvgl.STYLE_LINE_DASH_WIDTH
    TEXT_ALIGN = _lvgl.STYLE_TEXT_ALIGN
    TEXT_LETTER_SPACE = _lvgl.STYLE_TEXT_LETTER_SPACE
    TEXT_LINE_SPACE = _lvgl.STYLE_TEXT_LINE_SPACE
    LINE_DASH_GAP = _lvgl.STYLE_LINE_DASH_GAP
    LINE_ROUNDED = _lvgl.STYLE_LINE_ROUNDED
    IMAGE_COLORKEY = _lvgl.STYLE_IMAGE_COLORKEY
    TEXT_OUTLINE_STROKE_WIDTH = _lvgl.STYLE_TEXT_OUTLINE_STROKE_WIDTH
    TEXT_OUTLINE_STROKE_OPA = _lvgl.STYLE_TEXT_OUTLINE_STROKE_OPA
    TEXT_OUTLINE_STROKE_COLOR = _lvgl.STYLE_TEXT_OUTLINE_STROKE_COLOR
    TEXT_DECOR = _lvgl.STYLE_TEXT_DECOR
    ARC_ROUNDED = _lvgl.STYLE_ARC_ROUNDED
    OPA = _lvgl.STYLE_OPA
    OPA_LAYERED = _lvgl.STYLE_OPA_LAYERED
    COLOR_FILTER_DSC = _lvgl.STYLE_COLOR_FILTER_DSC
    COLOR_FILTER_OPA = _lvgl.STYLE_COLOR_FILTER_OPA
    ANIM = _lvgl.STYLE_ANIM
    ANIM_DURATION = _lvgl.STYLE_ANIM_DURATION
    TRANSITION = _lvgl.STYLE_TRANSITION
    RADIUS = _lvgl.STYLE_RADIUS
    BITMAP_MASK_SRC = _lvgl.STYLE_BITMAP_MASK_SRC
    BLEND_MODE = _lvgl.STYLE_BLEND_MODE
    ROTARY_SENSITIVITY = _lvgl.STYLE_ROTARY_SENSITIVITY
    TRANSLATE_RADIAL = _lvgl.STYLE_TRANSLATE_RADIAL
    CLIP_CORNER = _lvgl.STYLE_CLIP_CORNER
    BASE_DIR = _lvgl.STYLE_BASE_DIR
    RECOLOR = _lvgl.STYLE_RECOLOR
    RECOLOR_OPA = _lvgl.STYLE_RECOLOR_OPA
    LAYOUT = _lvgl.STYLE_LAYOUT
    BLUR_RADIUS = _lvgl.STYLE_BLUR_RADIUS
    BLUR_BACKDROP = _lvgl.STYLE_BLUR_BACKDROP
    BLUR_QUALITY = _lvgl.STYLE_BLUR_QUALITY
    DROP_SHADOW_RADIUS = _lvgl.STYLE_DROP_SHADOW_RADIUS
    DROP_SHADOW_OFFSET_X = _lvgl.STYLE_DROP_SHADOW_OFFSET_X
    DROP_SHADOW_OFFSET_Y = _lvgl.STYLE_DROP_SHADOW_OFFSET_Y
    DROP_SHADOW_COLOR = _lvgl.STYLE_DROP_SHADOW_COLOR
    DROP_SHADOW_OPA = _lvgl.STYLE_DROP_SHADOW_OPA
    DROP_SHADOW_QUALITY = _lvgl.STYLE_DROP_SHADOW_QUALITY
    TRANSFORM_SCALE_X = _lvgl.STYLE_TRANSFORM_SCALE_X
    TRANSFORM_SCALE_Y = _lvgl.STYLE_TRANSFORM_SCALE_Y
    TRANSFORM_PIVOT_X = _lvgl.STYLE_TRANSFORM_PIVOT_X
    TRANSFORM_PIVOT_Y = _lvgl.STYLE_TRANSFORM_PIVOT_Y
    TRANSFORM_ROTATION = _lvgl.STYLE_TRANSFORM_ROTATION
    TRANSFORM_SKEW_X = _lvgl.STYLE_TRANSFORM_SKEW_X
    TRANSFORM_SKEW_Y = _lvgl.STYLE_TRANSFORM_SKEW_Y
    FLEX_FLOW = _lvgl.STYLE_FLEX_FLOW
    FLEX_MAIN_PLACE = _lvgl.STYLE_FLEX_MAIN_PLACE
    FLEX_CROSS_PLACE = _lvgl.STYLE_FLEX_CROSS_PLACE
    FLEX_TRACK_PLACE = _lvgl.STYLE_FLEX_TRACK_PLACE
    FLEX_GROW = _lvgl.STYLE_FLEX_GROW
    GRID_COLUMN_DSC_ARRAY = _lvgl.STYLE_GRID_COLUMN_DSC_ARRAY
    GRID_ROW_DSC_ARRAY = _lvgl.STYLE_GRID_ROW_DSC_ARRAY
    GRID_COLUMN_ALIGN = _lvgl.STYLE_GRID_COLUMN_ALIGN
    GRID_ROW_ALIGN = _lvgl.STYLE_GRID_ROW_ALIGN
    GRID_CELL_COLUMN_POS = _lvgl.STYLE_GRID_CELL_COLUMN_POS
    GRID_CELL_COLUMN_SPAN = _lvgl.STYLE_GRID_CELL_COLUMN_SPAN
    GRID_CELL_X_ALIGN = _lvgl.STYLE_GRID_CELL_X_ALIGN
    GRID_CELL_ROW_POS = _lvgl.STYLE_GRID_CELL_ROW_POS
    GRID_CELL_ROW_SPAN = _lvgl.STYLE_GRID_CELL_ROW_SPAN
    GRID_CELL_Y_ALIGN = _lvgl.STYLE_GRID_CELL_Y_ALIGN
    LAST_BUILT_IN_PROP = _lvgl.STYLE_LAST_BUILT_IN_PROP
    NUM_BUILT_IN_PROPS = _lvgl.STYLE_NUM_BUILT_IN_PROPS
    STATE_CMP_SAME = _lvgl.STYLE_STATE_CMP_SAME
    STATE_CMP_DIFF_REDRAW = _lvgl.STYLE_STATE_CMP_DIFF_REDRAW
    STATE_CMP_DIFF_DRAW_PAD = _lvgl.STYLE_STATE_CMP_DIFF_DRAW_PAD
    STATE_CMP_DIFF_LAYOUT = _lvgl.STYLE_STATE_CMP_DIFF_LAYOUT


class EVENT:
    ALL = _lvgl.EVENT_ALL
    PRESSED = _lvgl.EVENT_PRESSED
    PRESSING = _lvgl.EVENT_PRESSING
    PRESS_LOST = _lvgl.EVENT_PRESS_LOST
    SHORT_CLICKED = _lvgl.EVENT_SHORT_CLICKED
    SINGLE_CLICKED = _lvgl.EVENT_SINGLE_CLICKED
    DOUBLE_CLICKED = _lvgl.EVENT_DOUBLE_CLICKED
    TRIPLE_CLICKED = _lvgl.EVENT_TRIPLE_CLICKED
    LONG_PRESSED = _lvgl.EVENT_LONG_PRESSED
    LONG_PRESSED_REPEAT = _lvgl.EVENT_LONG_PRESSED_REPEAT
    CLICKED = _lvgl.EVENT_CLICKED
    RELEASED = _lvgl.EVENT_RELEASED
    SCROLL_BEGIN = _lvgl.EVENT_SCROLL_BEGIN
    SCROLL_THROW_BEGIN = _lvgl.EVENT_SCROLL_THROW_BEGIN
    SCROLL_END = _lvgl.EVENT_SCROLL_END
    SCROLL = _lvgl.EVENT_SCROLL
    GESTURE = _lvgl.EVENT_GESTURE
    KEY = _lvgl.EVENT_KEY
    ROTARY = _lvgl.EVENT_ROTARY
    FOCUSED = _lvgl.EVENT_FOCUSED
    DEFOCUSED = _lvgl.EVENT_DEFOCUSED
    LEAVE = _lvgl.EVENT_LEAVE
    HIT_TEST = _lvgl.EVENT_HIT_TEST
    INDEV_RESET = _lvgl.EVENT_INDEV_RESET
    HOVER_OVER = _lvgl.EVENT_HOVER_OVER
    HOVER_LEAVE = _lvgl.EVENT_HOVER_LEAVE
    COVER_CHECK = _lvgl.EVENT_COVER_CHECK
    REFR_EXT_DRAW_SIZE = _lvgl.EVENT_REFR_EXT_DRAW_SIZE
    DRAW_MAIN_BEGIN = _lvgl.EVENT_DRAW_MAIN_BEGIN
    DRAW_MAIN = _lvgl.EVENT_DRAW_MAIN
    DRAW_MAIN_END = _lvgl.EVENT_DRAW_MAIN_END
    DRAW_POST_BEGIN = _lvgl.EVENT_DRAW_POST_BEGIN
    DRAW_POST = _lvgl.EVENT_DRAW_POST
    DRAW_POST_END = _lvgl.EVENT_DRAW_POST_END
    DRAW_TASK_ADDED = _lvgl.EVENT_DRAW_TASK_ADDED
    VALUE_CHANGED = _lvgl.EVENT_VALUE_CHANGED
    INSERT = _lvgl.EVENT_INSERT
    REFRESH = _lvgl.EVENT_REFRESH
    READY = _lvgl.EVENT_READY
    CANCEL = _lvgl.EVENT_CANCEL
    STATE_CHANGED = _lvgl.EVENT_STATE_CHANGED
    CREATE = _lvgl.EVENT_CREATE
    DELETE = _lvgl.EVENT_DELETE
    CHILD_CHANGED = _lvgl.EVENT_CHILD_CHANGED
    CHILD_CREATED = _lvgl.EVENT_CHILD_CREATED
    CHILD_DELETED = _lvgl.EVENT_CHILD_DELETED
    SCREEN_UNLOAD_START = _lvgl.EVENT_SCREEN_UNLOAD_START
    SCREEN_LOAD_START = _lvgl.EVENT_SCREEN_LOAD_START
    SCREEN_LOADED = _lvgl.EVENT_SCREEN_LOADED
    SCREEN_UNLOADED = _lvgl.EVENT_SCREEN_UNLOADED
    SIZE_CHANGED = _lvgl.EVENT_SIZE_CHANGED
    STYLE_CHANGED = _lvgl.EVENT_STYLE_CHANGED
    LAYOUT_CHANGED = _lvgl.EVENT_LAYOUT_CHANGED
    GET_SELF_SIZE = _lvgl.EVENT_GET_SELF_SIZE
    INVALIDATE_AREA = _lvgl.EVENT_INVALIDATE_AREA
    RESOLUTION_CHANGED = _lvgl.EVENT_RESOLUTION_CHANGED
    COLOR_FORMAT_CHANGED = _lvgl.EVENT_COLOR_FORMAT_CHANGED
    REFR_REQUEST = _lvgl.EVENT_REFR_REQUEST
    REFR_START = _lvgl.EVENT_REFR_START
    REFR_READY = _lvgl.EVENT_REFR_READY
    RENDER_START = _lvgl.EVENT_RENDER_START
    RENDER_READY = _lvgl.EVENT_RENDER_READY
    FLUSH_START = _lvgl.EVENT_FLUSH_START
    FLUSH_FINISH = _lvgl.EVENT_FLUSH_FINISH
    FLUSH_WAIT_START = _lvgl.EVENT_FLUSH_WAIT_START
    FLUSH_WAIT_FINISH = _lvgl.EVENT_FLUSH_WAIT_FINISH
    UPDATE_LAYOUT_COMPLETED = _lvgl.EVENT_UPDATE_LAYOUT_COMPLETED
    VSYNC = _lvgl.EVENT_VSYNC
    VSYNC_REQUEST = _lvgl.EVENT_VSYNC_REQUEST
    LAST = _lvgl.EVENT_LAST
    PREPROCESS = _lvgl.EVENT_PREPROCESS
    MARKED_DELETING = _lvgl.EVENT_MARKED_DELETING


class DISPLAY_ROTATION:
    _0 = _lvgl.DISPLAY_ROTATION_0
    _90 = _lvgl.DISPLAY_ROTATION_90
    _180 = _lvgl.DISPLAY_ROTATION_180
    _270 = _lvgl.DISPLAY_ROTATION_270
    RENDER_MODE_PARTIAL = _lvgl.DISPLAY_RENDER_MODE_PARTIAL
    RENDER_MODE_DIRECT = _lvgl.DISPLAY_RENDER_MODE_DIRECT
    RENDER_MODE_FULL = _lvgl.DISPLAY_RENDER_MODE_FULL


class SCROLLBAR_MODE:
    OFF = _lvgl.SCROLLBAR_MODE_OFF
    ON = _lvgl.SCROLLBAR_MODE_ON
    ACTIVE = _lvgl.SCROLLBAR_MODE_ACTIVE
    AUTO = _lvgl.SCROLLBAR_MODE_AUTO


class SCROLL_SNAP:
    NONE = _lvgl.SCROLL_SNAP_NONE
    START = _lvgl.SCROLL_SNAP_START
    END = _lvgl.SCROLL_SNAP_END
    CENTER = _lvgl.SCROLL_SNAP_CENTER


class STATE:
    DEFAULT = _lvgl.STATE_DEFAULT
    ALT = _lvgl.STATE_ALT
    CHECKED = _lvgl.STATE_CHECKED
    FOCUSED = _lvgl.STATE_FOCUSED
    FOCUS_KEY = _lvgl.STATE_FOCUS_KEY
    EDITED = _lvgl.STATE_EDITED
    HOVERED = _lvgl.STATE_HOVERED
    PRESSED = _lvgl.STATE_PRESSED
    SCROLLED = _lvgl.STATE_SCROLLED
    DISABLED = _lvgl.STATE_DISABLED
    USER_1 = _lvgl.STATE_USER_1
    USER_2 = _lvgl.STATE_USER_2
    USER_3 = _lvgl.STATE_USER_3
    USER_4 = _lvgl.STATE_USER_4
    ANY = _lvgl.STATE_ANY


class PART:
    MAIN = _lvgl.PART_MAIN
    SCROLLBAR = _lvgl.PART_SCROLLBAR
    INDICATOR = _lvgl.PART_INDICATOR
    KNOB = _lvgl.PART_KNOB
    SELECTED = _lvgl.PART_SELECTED
    ITEMS = _lvgl.PART_ITEMS
    CURSOR = _lvgl.PART_CURSOR
    CUSTOM_FIRST = _lvgl.PART_CUSTOM_FIRST
    ANY = _lvgl.PART_ANY
    TEXTAREA_PLACEHOLDER = _lvgl.PART_TEXTAREA_PLACEHOLDER


class LAYER_TYPE:
    NONE = _lvgl.LAYER_TYPE_NONE
    SIMPLE = _lvgl.LAYER_TYPE_SIMPLE
    TRANSFORM = _lvgl.LAYER_TYPE_TRANSFORM


class KEY:
    UP = _lvgl.KEY_UP
    DOWN = _lvgl.KEY_DOWN
    RIGHT = _lvgl.KEY_RIGHT
    LEFT = _lvgl.KEY_LEFT
    ESC = _lvgl.KEY_ESC
    DEL = _lvgl.KEY_DEL
    BACKSPACE = _lvgl.KEY_BACKSPACE
    ENTER = _lvgl.KEY_ENTER
    NEXT = _lvgl.KEY_NEXT
    PREV = _lvgl.KEY_PREV
    HOME = _lvgl.KEY_HOME
    END = _lvgl.KEY_END


class GROUP_REFOCUS:
    POLICY_NEXT = _lvgl.GROUP_REFOCUS_POLICY_NEXT
    POLICY_PREV = _lvgl.GROUP_REFOCUS_POLICY_PREV


class INDEV_MODE:
    NONE = _lvgl.INDEV_MODE_NONE
    TIMER = _lvgl.INDEV_MODE_TIMER
    EVENT = _lvgl.INDEV_MODE_EVENT
    GESTURE_NONE = _lvgl.INDEV_GESTURE_NONE
    GESTURE_PINCH = _lvgl.INDEV_GESTURE_PINCH
    GESTURE_SWIPE = _lvgl.INDEV_GESTURE_SWIPE
    GESTURE_ROTATE = _lvgl.INDEV_GESTURE_ROTATE
    GESTURE_TWO_FINGERS_SWIPE = _lvgl.INDEV_GESTURE_TWO_FINGERS_SWIPE
    GESTURE_SCROLL = _lvgl.INDEV_GESTURE_SCROLL
    GESTURE_CNT = _lvgl.INDEV_GESTURE_CNT


class COVER_RES:
    COVER = _lvgl.COVER_RES_COVER
    NOT_COVER = _lvgl.COVER_RES_NOT_COVER
    MASKED = _lvgl.COVER_RES_MASKED


class SUBJECT_TYPE:
    INVALID = _lvgl.SUBJECT_TYPE_INVALID
    NONE = _lvgl.SUBJECT_TYPE_NONE
    INT = _lvgl.SUBJECT_TYPE_INT
    FLOAT = _lvgl.SUBJECT_TYPE_FLOAT
    POINTER = _lvgl.SUBJECT_TYPE_POINTER
    COLOR = _lvgl.SUBJECT_TYPE_COLOR
    GROUP = _lvgl.SUBJECT_TYPE_GROUP
    STRING = _lvgl.SUBJECT_TYPE_STRING


class GRIDNAV_CTRL:
    NONE = _lvgl.GRIDNAV_CTRL_NONE
    ROLLOVER = _lvgl.GRIDNAV_CTRL_ROLLOVER
    SCROLL_FIRST = _lvgl.GRIDNAV_CTRL_SCROLL_FIRST
    HORIZONTAL_MOVE_ONLY = _lvgl.GRIDNAV_CTRL_HORIZONTAL_MOVE_ONLY
    VERTICAL_MOVE_ONLY = _lvgl.GRIDNAV_CTRL_VERTICAL_MOVE_ONLY

_IMAGE_ALIGN_AUTO_TRANSFORM = _lvgl._IMAGE_ALIGN_AUTO_TRANSFORM

_obj_t = _lvgl._obj_t
_obj_class_t = _lvgl._obj_class_t
_group_t = _lvgl._group_t
_display_t = _lvgl._display_t
_layer_t = _lvgl._layer_t
_draw_unit_t = _lvgl._draw_unit_t
_draw_task_t = _lvgl._draw_task_t
_indev_t = _lvgl._indev_t
_event_t = _lvgl._event_t
_timer_t = _lvgl._timer_t
_theme_t = _lvgl._theme_t
_anim_t = _lvgl._anim_t
_anim_timeline_t = _lvgl._anim_timeline_t
_font_t = _lvgl._font_t
_font_class_t = _lvgl._font_class_t
_font_info_t = _lvgl._font_info_t
_font_manager_t = _lvgl._font_manager_t
_image_decoder_t = _lvgl._image_decoder_t
_image_decoder_dsc_t = _lvgl._image_decoder_dsc_t
_draw_image_dsc_t = _lvgl._draw_image_dsc_t
_fragment_t = _lvgl._fragment_t
_fragment_class_t = _lvgl._fragment_class_t
_fragment_managed_states_t = _lvgl._fragment_managed_states_t
_profiler_builtin_config_t = _lvgl._profiler_builtin_config_t
_rb_node_t = _lvgl._rb_node_t
_rb_t = _lvgl._rb_t
_color_filter_dsc_t = _lvgl._color_filter_dsc_t
_event_dsc_t = _lvgl._event_dsc_t
_cache_t = _lvgl._cache_t
_cache_entry_t = _lvgl._cache_entry_t
_fs_file_cache_t = _lvgl._fs_file_cache_t
_image_decoder_args_t = _lvgl._image_decoder_args_t
_image_cache_data_t = _lvgl._image_cache_data_t
_image_header_cache_data_t = _lvgl._image_header_cache_data_t
_draw_mask_t = _lvgl._draw_mask_t
_draw_label_hint_t = _lvgl._draw_label_hint_t
_draw_glyph_dsc_t = _lvgl._draw_glyph_dsc_t
_draw_image_sup_t = _lvgl._draw_image_sup_t
_draw_mask_rect_dsc_t = _lvgl._draw_mask_rect_dsc_t
_obj_style_t = _lvgl._obj_style_t
_obj_style_transition_dsc_t = _lvgl._obj_style_transition_dsc_t
_hit_test_info_t = _lvgl._hit_test_info_t
_cover_check_info_t = _lvgl._cover_check_info_t
_obj_spec_attr_t = _lvgl._obj_spec_attr_t
_image_t = _lvgl._image_t
_animimg_t = _lvgl._animimg_t
_arc_t = _lvgl._arc_t
_arclabel_t = _lvgl._arclabel_t
_label_t = _lvgl._label_t
_bar_anim_t = _lvgl._bar_anim_t
_bar_t = _lvgl._bar_t
_button_t = _lvgl._button_t
_buttonmatrix_t = _lvgl._buttonmatrix_t
_calendar_t = _lvgl._calendar_t
_canvas_t = _lvgl._canvas_t
_chart_series_t = _lvgl._chart_series_t
_chart_cursor_t = _lvgl._chart_cursor_t
_chart_t = _lvgl._chart_t
_checkbox_t = _lvgl._checkbox_t
_dropdown_t = _lvgl._dropdown_t
_dropdown_list_t = _lvgl._dropdown_list_t
_imagebutton_src_info_t = _lvgl._imagebutton_src_info_t
_imagebutton_t = _lvgl._imagebutton_t
_keyboard_t = _lvgl._keyboard_t
_led_t = _lvgl._led_t
_line_t = _lvgl._line_t
_menu_load_page_event_data_t = _lvgl._menu_load_page_event_data_t
_menu_history_t = _lvgl._menu_history_t
_menu_t = _lvgl._menu_t
_menu_page_t = _lvgl._menu_page_t
_msgbox_t = _lvgl._msgbox_t
_roller_t = _lvgl._roller_t
_scale_section_t = _lvgl._scale_section_t
_scale_t = _lvgl._scale_t
_slider_t = _lvgl._slider_t
_span_t = _lvgl._span_t
_spangroup_t = _lvgl._spangroup_t
_textarea_t = _lvgl._textarea_t
_spinbox_t = _lvgl._spinbox_t
_switch_t = _lvgl._switch_t
_table_cell_t = _lvgl._table_cell_t
_table_t = _lvgl._table_t
_tabview_t = _lvgl._tabview_t
_tileview_t = _lvgl._tileview_t
_tileview_tile_t = _lvgl._tileview_tile_t
_win_t = _lvgl._win_t
_spinner_t = _lvgl._spinner_t
_type_3dtexture_t = _lvgl._type_3dtexture_t
_gltf_t = _lvgl._gltf_t
_gltf_model_t = _lvgl._gltf_model_t
_gltf_model_node_t = _lvgl._gltf_model_node_t
_gltf_environment = _lvgl._gltf_environment
_gltf_ibl_sampler = _lvgl._gltf_ibl_sampler
_subject_t = _lvgl._subject_t
_observer_t = _lvgl._observer_t
_subject_increment_dsc_t = _lvgl._subject_increment_dsc_t
_monkey_config_t = _lvgl._monkey_config_t
_ime_pinyin_t = _lvgl._ime_pinyin_t
_file_explorer_t = _lvgl._file_explorer_t
_barcode_t = _lvgl._barcode_t
_qrcode_t = _lvgl._qrcode_t
_freetype_outline_vector_t = _lvgl._freetype_outline_vector_t
_freetype_outline_event_param_t = _lvgl._freetype_outline_event_param_t
_fpoint_t = _lvgl._fpoint_t
_matrix_t = _lvgl._matrix_t
_vector_path_t = _lvgl._vector_path_t
_vector_gradient_t = _lvgl._vector_gradient_t
_vector_fill_dsc_t = _lvgl._vector_fill_dsc_t
_vector_stroke_dsc_t = _lvgl._vector_stroke_dsc_t
_vector_path_ctx_t = _lvgl._vector_path_ctx_t
_draw_vector_dsc_t = _lvgl._draw_vector_dsc_t
_xkb_t = _lvgl._xkb_t
_libinput_event_t = _lvgl._libinput_event_t
_libinput_t = _lvgl._libinput_t
_draw_sw_unit_t = _lvgl._draw_sw_unit_t
_draw_sw_mask_common_dsc_t = _lvgl._draw_sw_mask_common_dsc_t
_draw_sw_mask_line_param_t = _lvgl._draw_sw_mask_line_param_t
_draw_sw_mask_angle_param_t = _lvgl._draw_sw_mask_angle_param_t
_draw_sw_mask_radius_param_t = _lvgl._draw_sw_mask_radius_param_t
_draw_sw_mask_fade_param_t = _lvgl._draw_sw_mask_fade_param_t
_draw_sw_mask_map_param_t = _lvgl._draw_sw_mask_map_param_t
_draw_sw_blend_dsc_t = _lvgl._draw_sw_blend_dsc_t
_draw_sw_blend_fill_dsc_t = _lvgl._draw_sw_blend_fill_dsc_t
_draw_sw_blend_image_dsc_t = _lvgl._draw_sw_blend_image_dsc_t
_draw_buf_handlers_t = _lvgl._draw_buf_handlers_t
_rlottie_t = _lvgl._rlottie_t
_ffmpeg_player_t = _lvgl._ffmpeg_player_t
_opengles_window_t = _lvgl._opengles_window_t
_opengles_window_texture_t = _lvgl._opengles_window_texture_t
_array_t = _lvgl._array_t
_iter_t = _lvgl._iter_t
_circle_buf_t = _lvgl._circle_buf_t
_draw_buf_t = _lvgl._draw_buf_t
sqrt_res_t = _lvgl.sqrt_res_t
anim_bezier3_para_t = _lvgl.anim_bezier3_para_t
_anim_timeline_dsc_t = _lvgl._anim_timeline_dsc_t
color_hsv_t = _lvgl.color_hsv_t
color16a_t = _lvgl.color16a_t
image_header_t = _lvgl.image_header_t
yuv_plane_t = _lvgl.yuv_plane_t
yuv_buf_t = _lvgl.yuv_buf_t
_tree_class_t = _lvgl._tree_class_t
_tree_node_t = _lvgl._tree_node_t
grad_stop_t = _lvgl.grad_stop_t
image_colorkey_t = _lvgl.image_colorkey_t
style_value_t = _lvgl.style_value_t
style_const_prop_t = _lvgl.style_const_prop_t
_fs_drv_t = _lvgl._fs_drv_t
draw_dsc_base_t = _lvgl.draw_dsc_base_t
indev_data_t = _lvgl.indev_data_t
subject_value_t = _lvgl.subject_value_t
binfont_font_src_t = _lvgl.binfont_font_src_t
font_fmt_txt_glyph_dsc_t = _lvgl.font_fmt_txt_glyph_dsc_t
font_fmt_txt_cmap_t = _lvgl.font_fmt_txt_cmap_t
font_fmt_txt_kern_pair_t = _lvgl.font_fmt_txt_kern_pair_t
font_fmt_txt_kern_classes_t = _lvgl.font_fmt_txt_kern_classes_t
font_fmt_txt_dsc_t = _lvgl.font_fmt_txt_dsc_t
builtin_font_src_t = _lvgl.builtin_font_src_t
calendar_date_t = _lvgl.calendar_date_t
_span_coords_t = _lvgl._span_coords_t
pinyin_dict_t = _lvgl.pinyin_dict_t
ime_pinyin_k9_py_str_t = _lvgl.ime_pinyin_k9_py_str_t
tiny_ttf_font_src_t = _lvgl.tiny_ttf_font_src_t
SDL_Window = _lvgl.SDL_Window
_demo_args = _lvgl._demo_args
obj_t = _lvgl.obj_t
draw_unit_t = _lvgl.draw_unit_t
font_class_t = _lvgl.font_class_t
font_manager_t = _lvgl.font_manager_t
fragment_t = _lvgl.fragment_t
fragment_class_t = _lvgl.fragment_class_t
fragment_managed_states_t = _lvgl.fragment_managed_states_t
profiler_builtin_config_t = _lvgl.profiler_builtin_config_t
cache_t = _lvgl.cache_t
cache_entry_t = _lvgl.cache_entry_t
fs_file_cache_t = _lvgl.fs_file_cache_t
image_decoder_args_t = _lvgl.image_decoder_args_t
image_cache_data_t = _lvgl.image_cache_data_t
image_header_cache_data_t = _lvgl.image_header_cache_data_t
draw_mask_t = _lvgl.draw_mask_t
draw_label_hint_t = _lvgl.draw_label_hint_t
draw_image_sup_t = _lvgl.draw_image_sup_t
draw_mask_rect_dsc_t = _lvgl.draw_mask_rect_dsc_t
obj_style_t = _lvgl.obj_style_t
obj_style_transition_dsc_t = _lvgl.obj_style_transition_dsc_t
hit_test_info_t = _lvgl.hit_test_info_t
cover_check_info_t = _lvgl.cover_check_info_t
obj_spec_attr_t = _lvgl.obj_spec_attr_t
image_t = _lvgl.image_t
animimg_t = _lvgl.animimg_t
arc_t = _lvgl.arc_t
arclabel_t = _lvgl.arclabel_t
label_t = _lvgl.label_t
bar_anim_t = _lvgl.bar_anim_t
bar_t = _lvgl.bar_t
button_t = _lvgl.button_t
buttonmatrix_t = _lvgl.buttonmatrix_t
calendar_t = _lvgl.calendar_t
canvas_t = _lvgl.canvas_t
chart_series_t = _lvgl.chart_series_t
chart_cursor_t = _lvgl.chart_cursor_t
chart_t = _lvgl.chart_t
checkbox_t = _lvgl.checkbox_t
dropdown_t = _lvgl.dropdown_t
dropdown_list_t = _lvgl.dropdown_list_t
imagebutton_src_info_t = _lvgl.imagebutton_src_info_t
imagebutton_t = _lvgl.imagebutton_t
keyboard_t = _lvgl.keyboard_t
led_t = _lvgl.led_t
line_t = _lvgl.line_t
menu_load_page_event_data_t = _lvgl.menu_load_page_event_data_t
menu_history_t = _lvgl.menu_history_t
menu_t = _lvgl.menu_t
menu_page_t = _lvgl.menu_page_t
msgbox_t = _lvgl.msgbox_t
roller_t = _lvgl.roller_t
scale_t = _lvgl.scale_t
slider_t = _lvgl.slider_t
spangroup_t = _lvgl.spangroup_t
textarea_t = _lvgl.textarea_t
spinbox_t = _lvgl.spinbox_t
switch_t = _lvgl.switch_t
table_cell_t = _lvgl.table_cell_t
table_t = _lvgl.table_t
tabview_t = _lvgl.tabview_t
tileview_t = _lvgl.tileview_t
tileview_tile_t = _lvgl.tileview_tile_t
win_t = _lvgl.win_t
spinner_t = _lvgl.spinner_t
type_3dtexture_t = _lvgl.type_3dtexture_t
gltf_t = _lvgl.gltf_t
gltf_model_t = _lvgl.gltf_model_t
gltf_model_node_t = _lvgl.gltf_model_node_t
gltf_environment_t = _lvgl.gltf_environment_t
gltf_ibl_sampler_t = _lvgl.gltf_ibl_sampler_t
subject_increment_dsc_t = _lvgl.subject_increment_dsc_t
monkey_config_t = _lvgl.monkey_config_t
ime_pinyin_t = _lvgl.ime_pinyin_t
file_explorer_t = _lvgl.file_explorer_t
barcode_t = _lvgl.barcode_t
qrcode_t = _lvgl.qrcode_t
freetype_outline_vector_t = _lvgl.freetype_outline_vector_t
freetype_outline_event_param_t = _lvgl.freetype_outline_event_param_t
fpoint_t = _lvgl.fpoint_t
matrix_t = _lvgl.matrix_t
vector_path_t = _lvgl.vector_path_t
vector_gradient_t = _lvgl.vector_gradient_t
vector_fill_dsc_t = _lvgl.vector_fill_dsc_t
vector_stroke_dsc_t = _lvgl.vector_stroke_dsc_t
vector_path_ctx_t = _lvgl.vector_path_ctx_t
draw_vector_dsc_t = _lvgl.draw_vector_dsc_t
xkb_t = _lvgl.xkb_t
libinput_event_t = _lvgl.libinput_event_t
libinput_t = _lvgl.libinput_t
draw_sw_unit_t = _lvgl.draw_sw_unit_t
draw_sw_mask_common_dsc_t = _lvgl.draw_sw_mask_common_dsc_t
draw_sw_mask_line_param_t = _lvgl.draw_sw_mask_line_param_t
draw_sw_mask_angle_param_t = _lvgl.draw_sw_mask_angle_param_t
draw_sw_mask_radius_param_t = _lvgl.draw_sw_mask_radius_param_t
draw_sw_mask_fade_param_t = _lvgl.draw_sw_mask_fade_param_t
draw_sw_mask_map_param_t = _lvgl.draw_sw_mask_map_param_t
draw_sw_blend_dsc_t = _lvgl.draw_sw_blend_dsc_t
draw_sw_blend_fill_dsc_t = _lvgl.draw_sw_blend_fill_dsc_t
draw_sw_blend_image_dsc_t = _lvgl.draw_sw_blend_image_dsc_t
rlottie_t = _lvgl.rlottie_t
ffmpeg_player_t = _lvgl.ffmpeg_player_t
opengles_window_t = _lvgl.opengles_window_t
opengles_window_texture_t = _lvgl.opengles_window_texture_t
anim_timeline_dsc_t = _lvgl.anim_timeline_dsc_t
span_coords_t = _lvgl.span_coords_t
img_dsc_t = _lvgl.img_dsc_t
disp_t = _lvgl.disp_t


_callback_object_handles = _lvgl._callback_object_handles
_callback_return_refs = _lvgl._callback_return_refs
_global_cb_store = _lvgl._global_cb_store
_global_cb_handles = _lvgl._global_cb_handles
obj_class = _lvgl.obj_class
image_class = _lvgl.image_class
animimg_class = _lvgl.animimg_class
arc_class = _lvgl.arc_class
arclabel_class = _lvgl.arclabel_class
label_class = _lvgl.label_class
bar_class = _lvgl.bar_class
button_class = _lvgl.button_class
buttonmatrix_class = _lvgl.buttonmatrix_class
calendar_class = _lvgl.calendar_class
calendar_header_arrow_class = _lvgl.calendar_header_arrow_class
calendar_header_dropdown_class = _lvgl.calendar_header_dropdown_class
canvas_class = _lvgl.canvas_class
chart_class = _lvgl.chart_class
checkbox_class = _lvgl.checkbox_class
dropdown_class = _lvgl.dropdown_class
dropdownlist_class = _lvgl.dropdownlist_class
gif_class = _lvgl.gif_class
imagebutton_class = _lvgl.imagebutton_class
keyboard_class = _lvgl.keyboard_class
led_class = _lvgl.led_class
line_class = _lvgl.line_class
list_class = _lvgl.list_class
list_text_class = _lvgl.list_text_class
list_button_class = _lvgl.list_button_class
menu_class = _lvgl.menu_class
menu_page_class = _lvgl.menu_page_class
menu_cont_class = _lvgl.menu_cont_class
menu_section_class = _lvgl.menu_section_class
menu_separator_class = _lvgl.menu_separator_class
menu_sidebar_cont_class = _lvgl.menu_sidebar_cont_class
menu_main_cont_class = _lvgl.menu_main_cont_class
menu_sidebar_header_cont_class = _lvgl.menu_sidebar_header_cont_class
menu_main_header_cont_class = _lvgl.menu_main_header_cont_class
msgbox_class = _lvgl.msgbox_class
msgbox_header_class = _lvgl.msgbox_header_class
msgbox_content_class = _lvgl.msgbox_content_class
msgbox_footer_class = _lvgl.msgbox_footer_class
msgbox_header_button_class = _lvgl.msgbox_header_button_class
msgbox_footer_button_class = _lvgl.msgbox_footer_button_class
msgbox_backdrop_class = _lvgl.msgbox_backdrop_class
roller_class = _lvgl.roller_class
scale_class = _lvgl.scale_class
slider_class = _lvgl.slider_class
spangroup_class = _lvgl.spangroup_class
textarea_class = _lvgl.textarea_class
spinbox_class = _lvgl.spinbox_class
spinner_class = _lvgl.spinner_class
switch_class = _lvgl.switch_class
table_class = _lvgl.table_class
tabview_class = _lvgl.tabview_class
tileview_class = _lvgl.tileview_class
tileview_tile_class = _lvgl.tileview_tile_class
win_class = _lvgl.win_class
ime_pinyin_class = _lvgl.ime_pinyin_class
file_explorer_class = _lvgl.file_explorer_class
barcode_class = _lvgl.barcode_class
qrcode_class = _lvgl.qrcode_class
screen_create_cb_t = _lvgl.screen_create_cb_t
tick_get_cb_t = _lvgl.tick_get_cb_t
delay_cb_t = _lvgl.delay_cb_t
timer_cb_t = _lvgl.timer_cb_t
timer_handler_resume_cb_t = _lvgl.timer_handler_resume_cb_t
async_cb_t = _lvgl.async_cb_t
anim_path_cb_t = _lvgl.anim_path_cb_t
anim_custom_exec_cb_t = _lvgl.anim_custom_exec_cb_t
anim_completed_cb_t = _lvgl.anim_completed_cb_t
anim_start_cb_t = _lvgl.anim_start_cb_t
anim_get_value_cb_t = _lvgl.anim_get_value_cb_t
anim_deleted_cb_t = _lvgl.anim_deleted_cb_t
color_filter_cb_t = _lvgl.color_filter_cb_t
draw_buf_malloc_cb_t = _lvgl.draw_buf_malloc_cb_t
draw_buf_free_cb_t = _lvgl.draw_buf_free_cb_t
draw_buf_copy_cb_t = _lvgl.draw_buf_copy_cb_t
draw_buf_align_cb_t = _lvgl.draw_buf_align_cb_t
draw_buf_cache_operation_cb_t = _lvgl.draw_buf_cache_operation_cb_t
draw_buf_width_to_stride_cb_t = _lvgl.draw_buf_width_to_stride_cb_t
circle_buf_fill_cb_t = _lvgl.circle_buf_fill_cb_t
tree_constructor_cb_t = _lvgl.tree_constructor_cb_t
tree_destructor_cb_t = _lvgl.tree_destructor_cb_t
tree_traverse_cb_t = _lvgl.tree_traverse_cb_t
tree_before_cb_t = _lvgl.tree_before_cb_t
tree_after_cb_t = _lvgl.tree_after_cb_t
layout_update_cb_t = _lvgl.layout_update_cb_t
layout_get_min_size_cb_t = _lvgl.layout_get_min_size_cb_t
event_cb_t = _lvgl.event_cb_t
display_flush_cb_t = _lvgl.display_flush_cb_t
display_flush_wait_cb_t = _lvgl.display_flush_wait_cb_t
obj_tree_walk_cb_t = _lvgl.obj_tree_walk_cb_t
fs_drv_ready_cb_t = _lvgl.fs_drv_ready_cb_t
fs_drv_remove_cb_t = _lvgl.fs_drv_remove_cb_t
fs_drv_open_cb_t = _lvgl.fs_drv_open_cb_t
fs_drv_close_cb_t = _lvgl.fs_drv_close_cb_t
fs_drv_read_cb_t = _lvgl.fs_drv_read_cb_t
fs_drv_write_cb_t = _lvgl.fs_drv_write_cb_t
fs_drv_seek_cb_t = _lvgl.fs_drv_seek_cb_t
fs_drv_tell_cb_t = _lvgl.fs_drv_tell_cb_t
fs_drv_dir_open_cb_t = _lvgl.fs_drv_dir_open_cb_t
fs_drv_dir_read_cb_t = _lvgl.fs_drv_dir_read_cb_t
fs_drv_dir_close_cb_t = _lvgl.fs_drv_dir_close_cb_t
image_decoder_info_f_t = _lvgl.image_decoder_info_f_t
image_decoder_open_f_t = _lvgl.image_decoder_open_f_t
image_decoder_get_area_cb_t = _lvgl.image_decoder_get_area_cb_t
image_decoder_close_f_t = _lvgl.image_decoder_close_f_t
draw_glyph_cb_t = _lvgl.draw_glyph_cb_t
obj_class_event_cb_t = _lvgl.obj_class_event_cb_t
group_focus_cb_t = _lvgl.group_focus_cb_t
group_edge_cb_t = _lvgl.group_edge_cb_t
indev_read_cb_t = _lvgl.indev_read_cb_t
indev_key_remap_cb_t = _lvgl.indev_key_remap_cb_t
observer_cb_t = _lvgl.observer_cb_t
imgfont_get_path_cb_t = _lvgl.imgfont_get_path_cb_t
buttonmatrix_button_draw_cb_t = _lvgl.buttonmatrix_button_draw_cb_t
theme_apply_cb_t = _lvgl.theme_apply_cb_t
font_montserrat_12_subpx = _lvgl.font_montserrat_12_subpx
font_montserrat_28_compressed = _lvgl.font_montserrat_28_compressed
font_dejavu_16_persian_hebrew = _lvgl.font_dejavu_16_persian_hebrew
font_simsun_16_cjk = _lvgl.font_simsun_16_cjk
font_unscii_8 = _lvgl.font_unscii_8
font_unscii_16 = _lvgl.font_unscii_16
font_montserrat_8 = _lvgl.font_montserrat_8
font_montserrat_10 = _lvgl.font_montserrat_10
font_montserrat_12 = _lvgl.font_montserrat_12
font_montserrat_14 = _lvgl.font_montserrat_14
font_montserrat_16 = _lvgl.font_montserrat_16
font_montserrat_18 = _lvgl.font_montserrat_18
font_montserrat_20 = _lvgl.font_montserrat_20
font_montserrat_22 = _lvgl.font_montserrat_22
font_montserrat_24 = _lvgl.font_montserrat_24
font_montserrat_26 = _lvgl.font_montserrat_26
font_montserrat_28 = _lvgl.font_montserrat_28
font_montserrat_30 = _lvgl.font_montserrat_30
font_montserrat_32 = _lvgl.font_montserrat_32
font_montserrat_34 = _lvgl.font_montserrat_34
font_montserrat_36 = _lvgl.font_montserrat_36
font_montserrat_38 = _lvgl.font_montserrat_38
font_montserrat_40 = _lvgl.font_montserrat_40
font_montserrat_42 = _lvgl.font_montserrat_42
font_montserrat_44 = _lvgl.font_montserrat_44
font_montserrat_46 = _lvgl.font_montserrat_46
font_montserrat_48 = _lvgl.font_montserrat_48



def _make_callback_object_handle(py_obj: "empty") -> "empty":
    return _lvgl._make_callback_object_handle(py_obj)


def _release_callback_object_handle(c_obj: "empty") -> "empty":
    return _lvgl._release_callback_object_handle(c_obj)


def binding_version() -> "empty":
    return _lvgl.binding_version()


def sdl_get_display_size(display_index: "int") -> "empty":
    return _lvgl.sdl_get_display_size(display_index)


def _make_c_array(py_obj: "empty", c_type: "empty") -> "empty":
    return _lvgl._make_c_array(py_obj, c_type)


def _get_py_callback_ptr(c_obj: "empty", c_type: "empty") -> "empty":
    return _lvgl._get_py_callback_ptr(c_obj, c_type)


def _get_callback_return(py_obj: "empty", c_type: "empty", is_pointer: "empty") -> "empty":
    return _lvgl._get_callback_return(py_obj, c_type, is_pointer)


def anim_exec_xcb_t() -> None:
    return _lvgl.anim_exec_xcb_t()


def rb_compare_t(a: None, b: None) -> _lvgl.rb_compare_res_t:
    return _lvgl.rb_compare_t(a, b)


def iter_next_cb(instance: None, context: None, elem: None) -> _lvgl.result_t:
    return _lvgl.iter_next_cb(instance, context, elem)


def iter_inspect_cb(elem: None) -> None:
    return _lvgl.iter_inspect_cb(elem)


def image_decoder_custom_draw_t(layer: "layer_t", dsc: "image_decoder_dsc_t", coords: "area_t", draw_dsc: "draw_image_dsc_t", clip_area: "area_t") -> None:
    return _lvgl.image_decoder_custom_draw_t(layer, dsc, coords, draw_dsc, clip_area)


def init() -> None:
    return _lvgl.init()


def deinit() -> None:
    return _lvgl.deinit()


def is_initialized() -> _lvgl._Bool:
    return _lvgl.is_initialized()


def memcpy(dst: None, src: None, len: _lvgl.size_t) -> "Any":
    return _lvgl.memcpy(dst, src, len)


def memset(dst: None, v: _lvgl.uint8_t, len: _lvgl.size_t) -> None:
    return _lvgl.memset(dst, v, len)


def memmove(dst: None, src: None, len: _lvgl.size_t) -> "Any":
    return _lvgl.memmove(dst, src, len)


def memcmp(p1: None, p2: None, len: _lvgl.size_t) -> _lvgl.int_:
    return _lvgl.memcmp(p1, p2, len)


def memzero(dst: None, len: _lvgl.size_t) -> None:
    return _lvgl.memzero(dst, len)


def strlen(str: _lvgl.char) -> _lvgl.size_t:
    return _lvgl.strlen(str)


def strnlen(str: _lvgl.char, max_len: _lvgl.size_t) -> _lvgl.size_t:
    return _lvgl.strnlen(str, max_len)


def strlcpy(dst: _lvgl.char, src: _lvgl.char, dst_size: _lvgl.size_t) -> _lvgl.size_t:
    return _lvgl.strlcpy(dst, src, dst_size)


def strncpy(dst: _lvgl.char, src: _lvgl.char, dest_size: _lvgl.size_t) -> _lvgl.char:
    return _lvgl.strncpy(dst, src, dest_size)


def strcpy(dst: _lvgl.char, src: _lvgl.char) -> _lvgl.char:
    return _lvgl.strcpy(dst, src)


def strcmp(s1: _lvgl.char, s2: _lvgl.char) -> _lvgl.int_:
    return _lvgl.strcmp(s1, s2)


def strncmp(s1: _lvgl.char, s2: _lvgl.char, len: _lvgl.size_t) -> _lvgl.int_:
    return _lvgl.strncmp(s1, s2, len)


def streq(s1: _lvgl.char, s2: _lvgl.char) -> _lvgl._Bool:
    return _lvgl.streq(s1, s2)


def strdup(src: _lvgl.char) -> _lvgl.char:
    return _lvgl.strdup(src)


def strndup(src: _lvgl.char, max_len: _lvgl.size_t) -> _lvgl.char:
    return _lvgl.strndup(src, max_len)


def strcat(dst: _lvgl.char, src: _lvgl.char) -> _lvgl.char:
    return _lvgl.strcat(dst, src)


def strncat(dst: _lvgl.char, src: _lvgl.char, src_len: _lvgl.size_t) -> _lvgl.char:
    return _lvgl.strncat(dst, src, src_len)


def strchr(str: _lvgl.char, c: _lvgl.int_) -> _lvgl.char:
    return _lvgl.strchr(str, c)


def mem_init() -> None:
    return _lvgl.mem_init()


def mem_deinit() -> None:
    return _lvgl.mem_deinit()


def mem_add_pool(mem: None, bytes: _lvgl.size_t) -> "mem_pool_t":
    return _lvgl.mem_add_pool(mem, bytes)


def mem_remove_pool(pool: "mem_pool_t") -> None:
    return _lvgl.mem_remove_pool(pool)


def malloc(size: _lvgl.size_t) -> "Any":
    return _lvgl.malloc(size)


def calloc(num: _lvgl.size_t, size: _lvgl.size_t) -> "Any":
    return _lvgl.calloc(num, size)


def zalloc(size: _lvgl.size_t) -> "Any":
    return _lvgl.zalloc(size)


def malloc_zeroed(size: _lvgl.size_t) -> "Any":
    return _lvgl.malloc_zeroed(size)


def free(data: None) -> None:
    return _lvgl.free(data)


def realloc(data_p: None, new_size: _lvgl.size_t) -> "Any":
    return _lvgl.realloc(data_p, new_size)


def reallocf(data_p: None, new_size: _lvgl.size_t) -> "Any":
    return _lvgl.reallocf(data_p, new_size)


def malloc_core(size: _lvgl.size_t) -> "Any":
    return _lvgl.malloc_core(size)


def free_core(p: None) -> None:
    return _lvgl.free_core(p)


def realloc_core(p: None, new_size: _lvgl.size_t) -> "Any":
    return _lvgl.realloc_core(p, new_size)


def mem_test_core() -> _lvgl.result_t:
    return _lvgl.mem_test_core()


def mem_test() -> _lvgl.result_t:
    return _lvgl.mem_test()


def snprintf(buffer: _lvgl.char, count: _lvgl.size_t, format: _lvgl.char, *args) -> _lvgl.int_:
    return _lvgl.snprintf(buffer, count, format, *args)


def tick_inc(tick_period: _lvgl.uint32_t) -> None:
    return _lvgl.tick_inc(tick_period)


def tick_get() -> _lvgl.uint32_t:
    return _lvgl.tick_get()


def tick_elaps(prev_tick: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.tick_elaps(prev_tick)


def tick_diff(tick: _lvgl.uint32_t, prev_tick: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.tick_diff(tick, prev_tick)


def delay_ms(ms: _lvgl.uint32_t) -> None:
    return _lvgl.delay_ms(ms)


def delay_set_cb(cb: "delay_cb_t") -> None:
    return _lvgl.delay_set_cb(cb)


def tick_set_cb(cb: "tick_get_cb_t") -> None:
    return _lvgl.tick_set_cb(cb)


def tick_get_cb() -> "tick_get_cb_t":
    return _lvgl.tick_get_cb()


def timer_handler() -> _lvgl.uint32_t:
    return _lvgl.timer_handler()


def timer_handler_run_in_period(period: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.timer_handler_run_in_period(period)


def timer_periodic_handler() -> None:
    return _lvgl.timer_periodic_handler()


def timer_handler_set_resume_cb(cb: "timer_handler_resume_cb_t", data: None) -> None:
    return _lvgl.timer_handler_set_resume_cb(cb, data)


def timer_create_basic() -> "timer_t":
    return _lvgl.timer_create_basic()


def timer_enable(en: _lvgl._Bool) -> None:
    return _lvgl.timer_enable(en)


def timer_get_idle() -> _lvgl.uint32_t:
    return _lvgl.timer_get_idle()


def timer_get_time_until_next() -> _lvgl.uint32_t:
    return _lvgl.timer_get_time_until_next()


def trigo_sin(angle: _lvgl.int16_t) -> _lvgl.int32_t:
    return _lvgl.trigo_sin(angle)


def trigo_cos(angle: _lvgl.int16_t) -> _lvgl.int32_t:
    return _lvgl.trigo_cos(angle)


def cubic_bezier(x: _lvgl.int32_t, x1: _lvgl.int32_t, y1: _lvgl.int32_t, x2: _lvgl.int32_t, y2: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.cubic_bezier(x, x1, y1, x2, y2)


def bezier3(t: _lvgl.int32_t, u0: _lvgl.int32_t, u1: _lvgl.uint32_t, u2: _lvgl.int32_t, u3: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.bezier3(t, u0, u1, u2, u3)


def atan2(x: _lvgl.int_, y: _lvgl.int_) -> _lvgl.uint16_t:
    return _lvgl.atan2(x, y)


def sqrt(x: _lvgl.uint32_t, q: _lvgl.sqrt_res_t, mask: _lvgl.uint32_t) -> None:
    return _lvgl.sqrt(x, q, mask)


def sqrt32(x: _lvgl.uint32_t) -> _lvgl.int32_t:
    return _lvgl.sqrt32(x)


def sqr(x: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.sqr(x)


def pow(base: _lvgl.int64_t, exp: _lvgl.int8_t) -> _lvgl.int64_t:
    return _lvgl.pow(base, exp)


def map(x: _lvgl.int32_t, min_in: _lvgl.int32_t, max_in: _lvgl.int32_t, min_out: _lvgl.int32_t, max_out: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.map(x, min_in, max_in, min_out, max_out)


def rand_set_seed(seed: _lvgl.uint32_t) -> None:
    return _lvgl.rand_set_seed(seed)


def rand(min: _lvgl.uint32_t, max: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.rand(min, max)


def async_call(async_xcb: "async_cb_t", user_data: "Any") -> _lvgl.result_t:
    return _lvgl.async_call(async_xcb, user_data)


def async_call_cancel(async_xcb: "async_cb_t", user_data: "Any") -> _lvgl.result_t:
    return _lvgl.async_call_cancel(async_xcb, user_data)


def anim_delete(var: None, exec_cb: "anim_exec_xcb_t") -> _lvgl._Bool:
    return _lvgl.anim_delete(var, exec_cb)


def anim_delete_all() -> None:
    return _lvgl.anim_delete_all()


def anim_get(var: None, exec_cb: "anim_exec_xcb_t") -> "anim_t":
    return _lvgl.anim_get(var, exec_cb)


def anim_get_timer() -> "timer_t":
    return _lvgl.anim_get_timer()


def anim_count_running() -> _lvgl.uint16_t:
    return _lvgl.anim_count_running()


def anim_speed(speed: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.anim_speed(speed)


def anim_speed_clamped(speed: _lvgl.uint32_t, min_time: _lvgl.uint32_t, max_time: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.anim_speed_clamped(speed, min_time, max_time)


def anim_resolve_speed(speed: _lvgl.uint32_t, start: _lvgl.int32_t, end: _lvgl.int32_t) -> _lvgl.uint32_t:
    return _lvgl.anim_resolve_speed(speed, start, end)


def anim_speed_to_time(speed: _lvgl.uint32_t, start: _lvgl.int32_t, end: _lvgl.int32_t) -> _lvgl.uint32_t:
    return _lvgl.anim_speed_to_time(speed, start, end)


def anim_refr_now() -> None:
    return _lvgl.anim_refr_now()


def anim_path_linear(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_linear(a)


def anim_path_ease_in(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_ease_in(a)


def anim_path_ease_out(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_ease_out(a)


def anim_path_ease_in_out(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_ease_in_out(a)


def anim_path_overshoot(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_overshoot(a)


def anim_path_bounce(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_bounce(a)


def anim_path_step(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_step(a)


def anim_path_custom_bezier3(a: "anim_t") -> _lvgl.int32_t:
    return _lvgl.anim_path_custom_bezier3(a)


def pct(x: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.pct(x)


def pct_to_px(v: _lvgl.int32_t, base: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.pct_to_px(v, base)


def color_format_get_bpp(cf: _lvgl.color_format_t) -> _lvgl.uint8_t:
    return _lvgl.color_format_get_bpp(cf)


def color_format_get_size(cf: _lvgl.color_format_t) -> _lvgl.uint8_t:
    return _lvgl.color_format_get_size(cf)


def color_format_has_alpha(src_cf: _lvgl.color_format_t) -> _lvgl._Bool:
    return _lvgl.color_format_has_alpha(src_cf)


def color_hex(c: _lvgl.uint32_t) -> "color_t":
    return _lvgl.color_hex(c)


def color_make(r: _lvgl.uint8_t, g: _lvgl.uint8_t, b: _lvgl.uint8_t) -> "color_t":
    return _lvgl.color_make(r, g, b)


def color32_make(r: _lvgl.uint8_t, g: _lvgl.uint8_t, b: _lvgl.uint8_t, a: _lvgl.uint8_t) -> "color32_t":
    return _lvgl.color32_make(r, g, b, a)


def color_hex3(c: _lvgl.uint32_t) -> "color_t":
    return _lvgl.color_hex3(c)


def color_16_16_mix(c1: _lvgl.uint16_t, c2: _lvgl.uint16_t, mix: _lvgl.uint8_t) -> _lvgl.uint16_t:
    return _lvgl.color_16_16_mix(c1, c2, mix)


def color_hsv_to_rgb(h: _lvgl.uint16_t, s: _lvgl.uint8_t, v: _lvgl.uint8_t) -> "color_t":
    return _lvgl.color_hsv_to_rgb(h, s, v)


def color_rgb_to_hsv(r8: _lvgl.uint8_t, g8: _lvgl.uint8_t, b8: _lvgl.uint8_t) -> "color_hsv_t":
    return _lvgl.color_rgb_to_hsv(r8, g8, b8)


def color_white() -> "color_t":
    return _lvgl.color_white()


def color_black() -> "color_t":
    return _lvgl.color_black()


def color_premultiply(c: "color32_t") -> None:
    return _lvgl.color_premultiply(c)


def color24_luminance(c: _lvgl.uint8_t) -> _lvgl.uint8_t:
    return _lvgl.color24_luminance(c)


def color_swap_16(c: _lvgl.uint16_t) -> _lvgl.uint16_t:
    return _lvgl.color_swap_16(c)


def palette_main(p: _lvgl.palette_t) -> "color_t":
    return _lvgl.palette_main(p)


def palette_lighten(p: _lvgl.palette_t, lvl: _lvgl.uint8_t) -> "color_t":
    return _lvgl.palette_lighten(p, lvl)


def palette_darken(p: _lvgl.palette_t, lvl: _lvgl.uint8_t) -> "color_t":
    return _lvgl.palette_darken(p, lvl)


def color_mix32(fg: "color32_t", bg: "color32_t") -> "color32_t":
    return _lvgl.color_mix32(fg, bg)


def color_mix32_premultiplied(fg: "color32_t", bg: "color32_t") -> "color32_t":
    return _lvgl.color_mix32_premultiplied(fg, bg)


def color_over32(fg: "color32_t", bg: "color32_t") -> "color32_t":
    return _lvgl.color_over32(fg, bg)


def draw_buf_get_handlers() -> "draw_buf_handlers_t":
    return _lvgl.draw_buf_get_handlers()


def draw_buf_get_font_handlers() -> "draw_buf_handlers_t":
    return _lvgl.draw_buf_get_font_handlers()


def draw_buf_get_image_handlers() -> "draw_buf_handlers_t":
    return _lvgl.draw_buf_get_image_handlers()


def draw_buf_align(buf: None, color_format: _lvgl.color_format_t) -> "Any":
    return _lvgl.draw_buf_align(buf, color_format)


def draw_buf_width_to_stride(w: _lvgl.uint32_t, color_format: _lvgl.color_format_t) -> _lvgl.uint32_t:
    return _lvgl.draw_buf_width_to_stride(w, color_format)


def utils_bsearch(key: None, base: None, n: _lvgl.size_t, size: _lvgl.size_t, cmp: _lvgl.int_) -> "Any":
    return _lvgl.utils_bsearch(key, base, n, size, cmp)


def swap_bytes_32(x: _lvgl.uint32_t) -> _lvgl.uint32_t:
    return _lvgl.swap_bytes_32(x)


def swap_bytes_16(x: _lvgl.uint16_t) -> _lvgl.uint16_t:
    return _lvgl.swap_bytes_16(x)


def circle_buf_create_from_buf(buf: None, capacity: _lvgl.uint32_t, element_size: _lvgl.uint32_t) -> "circle_buf_t":
    return _lvgl.circle_buf_create_from_buf(buf, capacity, element_size)


def circle_buf_create_from_array(array: "array_t") -> "circle_buf_t":
    return _lvgl.circle_buf_create_from_array(array)


def lock() -> None:
    return _lvgl.lock()


def lock_isr() -> _lvgl.result_t:
    return _lvgl.lock_isr()


def unlock() -> None:
    return _lvgl.unlock()


def sleep_ms(ms: _lvgl.uint32_t) -> None:
    return _lvgl.sleep_ms(ms)


def font_get_default() -> "font_t":
    return _lvgl.font_get_default()


def text_get_size(size_res: _lvgl.point_t, text: _lvgl.char, font: "font_t", letter_space: _lvgl.int32_t, line_space: _lvgl.int32_t, max_width: _lvgl.int32_t, flag: _lvgl.text_flag_t) -> None:
    return _lvgl.text_get_size(size_res, text, font, letter_space, line_space, max_width, flag)


def bidi_calculate_align(align: _lvgl.text_align_t, base_dir: _lvgl.base_dir_t, txt: _lvgl.char) -> None:
    return _lvgl.bidi_calculate_align(align, base_dir, txt)


def bidi_set_custom_neutrals_static(neutrals: _lvgl.char) -> None:
    return _lvgl.bidi_set_custom_neutrals_static(neutrals)


def layout_register(cb: "layout_update_cb_t", user_data: "Any") -> _lvgl.uint32_t:
    return _lvgl.layout_register(cb, user_data)


def flex_init() -> None:
    return _lvgl.flex_init()


def grid_init() -> None:
    return _lvgl.grid_init()


def grid_fr(x: _lvgl.uint8_t) -> _lvgl.int32_t:
    return _lvgl.grid_fr(x)


def style_register_prop(flag: _lvgl.uint8_t) -> _lvgl.style_prop_t:
    return _lvgl.style_register_prop(flag)


def style_get_num_custom_props() -> _lvgl.style_prop_t:
    return _lvgl.style_get_num_custom_props()


def style_prop_get_default(prop: _lvgl.style_prop_t) -> "style_value_t":
    return _lvgl.style_prop_get_default(prop)


def style_get_prop_group(prop: _lvgl.style_prop_t) -> _lvgl.uint32_t:
    return _lvgl.style_get_prop_group(prop)


def style_prop_lookup_flags(prop: _lvgl.style_prop_t) -> _lvgl.uint8_t:
    return _lvgl.style_prop_lookup_flags(prop)


def style_prop_has_flag(prop: _lvgl.style_prop_t, flag: _lvgl.uint8_t) -> _lvgl._Bool:
    return _lvgl.style_prop_has_flag(prop, flag)


def event_register_id() -> _lvgl.uint32_t:
    return _lvgl.event_register_id()


def event_code_get_name(code: _lvgl.event_code_t) -> _lvgl.char:
    return _lvgl.event_code_get_name(code)


def display_get_default() -> "display_t":
    return _lvgl.display_get_default()


def screen_load(scr: "obj") -> None:
    return _lvgl.screen_load(scr)


def screen_load_anim(scr: "obj", anim_type: _lvgl.screen_load_anim_t, time: _lvgl.uint32_t, delay: _lvgl.uint32_t, auto_del: _lvgl._Bool) -> None:
    return _lvgl.screen_load_anim(scr, anim_type, time, delay, auto_del)


def screen_active() -> "obj":
    return _wrap_obj(_lvgl.screen_active())


def layer_top() -> "obj":
    return _wrap_obj(_lvgl.layer_top())


def layer_sys() -> "obj":
    return _wrap_obj(_lvgl.layer_sys())


def layer_bottom() -> "obj":
    return _wrap_obj(_lvgl.layer_bottom())


def dpx(n: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.dpx(n)


def obj_delete_anim_completed_cb(a: "anim_t") -> None:
    return _lvgl.obj_delete_anim_completed_cb(a)


def clamp_width(width: _lvgl.int32_t, min_width: _lvgl.int32_t, max_width: _lvgl.int32_t, ref_width: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.clamp_width(width, min_width, max_width, ref_width)


def clamp_height(height: _lvgl.int32_t, min_height: _lvgl.int32_t, max_height: _lvgl.int32_t, ref_height: _lvgl.int32_t) -> _lvgl.int32_t:
    return _lvgl.clamp_height(height, min_height, max_height, ref_height)


def obj_report_style_change(style: "style_t") -> None:
    return _lvgl.obj_report_style_change(style)


def obj_enable_style_refresh(en: _lvgl._Bool) -> None:
    return _lvgl.obj_enable_style_refresh(en)


def obj_style_get_selector_state(selector: _lvgl.style_selector_t) -> _lvgl.state_t:
    return _lvgl.obj_style_get_selector_state(selector)


def obj_style_get_selector_part(selector: _lvgl.style_selector_t) -> _lvgl.part_t:
    return _lvgl.obj_style_get_selector_part(selector)


def fs_get_drv(letter: _lvgl.char) -> "fs_drv_t":
    return _lvgl.fs_get_drv(letter)


def fs_remove_drive(letter: _lvgl.char) -> None:
    return _lvgl.fs_remove_drive(letter)


def fs_is_ready(letter: _lvgl.char) -> _lvgl._Bool:
    return _lvgl.fs_is_ready(letter)


def fs_path_get_size(path: _lvgl.char, size_res: _lvgl.uint32_t) -> _lvgl.fs_res_t:
    return _lvgl.fs_path_get_size(path, size_res)


def fs_load_to_buf(buf: None, buf_size: _lvgl.uint32_t, path: _lvgl.char) -> _lvgl.fs_res_t:
    return _lvgl.fs_load_to_buf(buf, buf_size, path)


def fs_load_with_alloc(path: _lvgl.char, size: _lvgl.uint32_t) -> "Any":
    return _lvgl.fs_load_with_alloc(path, size)


def fs_get_letters(buf: _lvgl.char) -> _lvgl.char:
    return _lvgl.fs_get_letters(buf)


def fs_get_ext(fn: _lvgl.char) -> _lvgl.char:
    return _lvgl.fs_get_ext(fn)


def fs_up(path: _lvgl.char) -> _lvgl.char:
    return _lvgl.fs_up(path)


def fs_get_last(path: _lvgl.char) -> _lvgl.char:
    return _lvgl.fs_get_last(path)


def fs_path_join(buf: _lvgl.char, buf_sz: _lvgl.size_t, base: _lvgl.char, end: _lvgl.char) -> _lvgl.int_:
    return _lvgl.fs_path_join(buf, buf_sz, base, end)


def image_decoder_get_info(src: None, header: "image_header_t") -> _lvgl.result_t:
    return _lvgl.image_decoder_get_info(src, header)


def draw_init() -> None:
    return _lvgl.draw_init()


def draw_deinit() -> None:
    return _lvgl.draw_deinit()


def draw_create_unit(size: _lvgl.size_t) -> "Any":
    return _lvgl.draw_create_unit(size)


def draw_add_task(layer: "layer_t", coords: "area_t", type: _lvgl.draw_task_type_t) -> "draw_task_t":
    return _lvgl.draw_add_task(layer, coords, type)


def draw_finalize_task_creation(layer: "layer_t", t: "draw_task_t") -> None:
    return _lvgl.draw_finalize_task_creation(layer, t)


def draw_dispatch() -> None:
    return _lvgl.draw_dispatch()


def draw_dispatch_layer(disp: "display_t", layer: "layer_t") -> _lvgl._Bool:
    return _lvgl.draw_dispatch_layer(disp, layer)


def draw_dispatch_wait_for_request() -> None:
    return _lvgl.draw_dispatch_wait_for_request()


def draw_wait_for_finish() -> None:
    return _lvgl.draw_wait_for_finish()


def draw_dispatch_request() -> None:
    return _lvgl.draw_dispatch_request()


def draw_get_unit_count() -> _lvgl.uint32_t:
    return _lvgl.draw_get_unit_count()


def draw_get_available_task(layer: "layer_t", t_prev: "draw_task_t", draw_unit_id: _lvgl.uint8_t) -> "draw_task_t":
    return _lvgl.draw_get_available_task(layer, t_prev, draw_unit_id)


def draw_get_next_available_task(layer: "layer_t", t_prev: "draw_task_t", draw_unit_id: _lvgl.uint8_t) -> "draw_task_t":
    return _lvgl.draw_get_next_available_task(layer, t_prev, draw_unit_id)


def draw_unit_send_event(name: _lvgl.char, code: _lvgl.event_code_t, param: None) -> None:
    return _lvgl.draw_unit_send_event(name, code, param)


def draw_fill(layer: "layer_t", dsc: "draw_fill_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_fill(layer, dsc, coords)


def draw_border(layer: "layer_t", dsc: "draw_border_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_border(layer, dsc, coords)


def draw_box_shadow(layer: "layer_t", dsc: "draw_box_shadow_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_box_shadow(layer, dsc, coords)


def draw_rect(layer: "layer_t", dsc: "draw_rect_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_rect(layer, dsc, coords)


def draw_label(layer: "layer_t", dsc: "draw_label_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_label(layer, dsc, coords)


def draw_character(layer: "layer_t", dsc: "draw_label_dsc_t", point: _lvgl.point_t, unicode_letter: _lvgl.uint32_t) -> None:
    return _lvgl.draw_character(layer, dsc, point, unicode_letter)


def draw_letter(layer: "layer_t", dsc: "draw_letter_dsc_t", point: _lvgl.point_t) -> None:
    return _lvgl.draw_letter(layer, dsc, point)


def draw_image(layer: "layer_t", dsc: "draw_image_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_image(layer, dsc, coords)


def draw_layer(layer: "layer_t", dsc: "draw_image_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_layer(layer, dsc, coords)


def image_src_get_type(src: None) -> _lvgl.image_src_t:
    return _lvgl.image_src_get_type(src)


def draw_line(layer: "layer_t", dsc: "draw_line_dsc_t") -> None:
    return _lvgl.draw_line(layer, dsc)


def draw_arc(layer: "layer_t", dsc: "draw_arc_dsc_t") -> None:
    return _lvgl.draw_arc(layer, dsc)


def draw_arc_get_area(x: _lvgl.int32_t, y: _lvgl.int32_t, radius: _lvgl.uint16_t, start_angle: _lvgl.value_precise_t, end_angle: _lvgl.value_precise_t, w: _lvgl.int32_t, rounded: _lvgl._Bool, area: "area_t") -> None:
    return _lvgl.draw_arc_get_area(x, y, radius, start_angle, end_angle, w, rounded, area)


def draw_triangle(layer: "layer_t", draw_dsc: "draw_triangle_dsc_t") -> None:
    return _lvgl.draw_triangle(layer, draw_dsc)


def draw_blur(layer: "layer_t", dsc: "draw_blur_dsc_t", coords: "area_t") -> None:
    return _lvgl.draw_blur(layer, dsc, coords)


def group_get_default() -> "group_t":
    return _lvgl.group_get_default()


def group_swap_obj(obj1: "obj", obj2: "obj") -> None:
    return _lvgl.group_swap_obj(obj1, obj2)


def group_remove_obj(obj: "obj") -> None:
    return _lvgl.group_remove_obj(obj)


def group_focus_obj(obj: "obj") -> None:
    return _lvgl.group_focus_obj(obj)


def group_get_count() -> _lvgl.uint32_t:
    return _lvgl.group_get_count()


def group_by_index(index: _lvgl.uint32_t) -> "group_t":
    return _lvgl.group_by_index(index)


def indev_create() -> "indev_t":
    return _lvgl.indev_create()


def indev_read_timer_cb(timer: "timer_t") -> None:
    return _lvgl.indev_read_timer_cb(timer)


def indev_active() -> "indev_t":
    return _lvgl.indev_active()


def indev_get_active_obj() -> "obj":
    return _wrap_obj(_lvgl.indev_get_active_obj())


def indev_search_obj(obj: "obj", point: _lvgl.point_t) -> "obj":
    return _wrap_obj(_lvgl.indev_search_obj(obj, point))


def refr_now(disp: "display_t") -> None:
    return _lvgl.refr_now(disp)


def obj_redraw(layer: "layer_t", obj: "obj") -> None:
    return _lvgl.obj_redraw(layer, obj)


def display_refr_timer(timer: "timer_t") -> None:
    return _lvgl.display_refr_timer(timer)


def gridnav_add(obj: "obj", ctrl: _lvgl.gridnav_ctrl_t) -> None:
    return _lvgl.gridnav_add(obj, ctrl)


def gridnav_remove(obj: "obj") -> None:
    return _lvgl.gridnav_remove(obj)


def gridnav_set_focused(cont: "obj", to_focus: "obj", anim_en: _lvgl.anim_enable_t) -> None:
    return _lvgl.gridnav_set_focused(cont, to_focus, anim_en)


def binfont_destroy(font: "font_t") -> None:
    return _lvgl.binfont_destroy(font)


def imgfont_destroy(font: "font_t") -> None:
    return _lvgl.imgfont_destroy(font)


def canvas_buf_size(w: _lvgl.int32_t, h: _lvgl.int32_t, bpp: _lvgl.uint8_t, stride: _lvgl.uint8_t) -> _lvgl.uint32_t:
    return _lvgl.canvas_buf_size(w, h, bpp, stride)


def gif_get_size(src: _lvgl.char, w: _lvgl.uint16_t, h: _lvgl.uint16_t) -> _lvgl._Bool:
    return _lvgl.gif_get_size(src, w, h)


def keyboard_def_event_cb(e: "event_t") -> None:
    return _lvgl.keyboard_def_event_cb(e)


def span_stack_init() -> None:
    return _lvgl.span_stack_init()


def span_stack_deinit() -> None:
    return _lvgl.span_stack_deinit()


def bin_decoder_init() -> None:
    return _lvgl.bin_decoder_init()


def bin_decoder_info(decoder: "image_decoder_t", dsc: "image_decoder_dsc_t", header: "image_header_t") -> _lvgl.result_t:
    return _lvgl.bin_decoder_info(decoder, dsc, header)


def bin_decoder_get_area(decoder: "image_decoder_t", dsc: "image_decoder_dsc_t", full_area: "area_t", decoded_area: "area_t") -> _lvgl.result_t:
    return _lvgl.bin_decoder_get_area(decoder, dsc, full_area, decoded_area)


def bin_decoder_open(decoder: "image_decoder_t", dsc: "image_decoder_dsc_t") -> _lvgl.result_t:
    return _lvgl.bin_decoder_open(decoder, dsc)


def bin_decoder_close(decoder: "image_decoder_t", dsc: "image_decoder_dsc_t") -> None:
    return _lvgl.bin_decoder_close(decoder, dsc)


def bmp_init() -> None:
    return _lvgl.bmp_init()


def bmp_deinit() -> None:
    return _lvgl.bmp_deinit()


def lodepng_init() -> None:
    return _lvgl.lodepng_init()


def lodepng_deinit() -> None:
    return _lvgl.lodepng_deinit()


def tiny_ttf_create_file(path: _lvgl.char, font_size: _lvgl.int32_t) -> "font_t":
    return _lvgl.tiny_ttf_create_file(path, font_size)


def tiny_ttf_create_file_ex(path: _lvgl.char, font_size: _lvgl.int32_t, kerning: _lvgl.font_kerning_t, cache_size: _lvgl.size_t) -> "font_t":
    return _lvgl.tiny_ttf_create_file_ex(path, font_size, kerning, cache_size)


def tiny_ttf_create_data(data: None, data_size: _lvgl.size_t, font_size: _lvgl.int32_t) -> "font_t":
    return _lvgl.tiny_ttf_create_data(data, data_size, font_size)


def tiny_ttf_create_data_ex(data: None, data_size: _lvgl.size_t, font_size: _lvgl.int32_t, kerning: _lvgl.font_kerning_t, cache_size: _lvgl.size_t) -> "font_t":
    return _lvgl.tiny_ttf_create_data_ex(data, data_size, font_size, kerning, cache_size)


def tiny_ttf_set_size(font: "font_t", font_size: _lvgl.int32_t) -> None:
    return _lvgl.tiny_ttf_set_size(font, font_size)


def tiny_ttf_destroy(font: "font_t") -> None:
    return _lvgl.tiny_ttf_destroy(font)


def draw_sw_i1_to_argb8888(buf_i1: None, buf_argb8888: None, width: _lvgl.uint32_t, height: _lvgl.uint32_t, buf_i1_stride: _lvgl.uint32_t, buf_argb8888_stride: _lvgl.uint32_t, index0_color: _lvgl.uint32_t, index1_color: _lvgl.uint32_t) -> None:
    return _lvgl.draw_sw_i1_to_argb8888(buf_i1, buf_argb8888, width, height, buf_i1_stride, buf_argb8888_stride, index0_color, index1_color)


def draw_sw_rgb565_swap(buf: None, buf_size_px: _lvgl.uint32_t) -> None:
    return _lvgl.draw_sw_rgb565_swap(buf, buf_size_px)


def draw_sw_i1_invert(buf: None, buf_size: _lvgl.uint32_t) -> None:
    return _lvgl.draw_sw_i1_invert(buf, buf_size)


def draw_sw_i1_convert_to_vtiled(buf: None, buf_size: _lvgl.uint32_t, width: _lvgl.uint32_t, height: _lvgl.uint32_t, out_buf: None, out_buf_size: _lvgl.uint32_t, bit_order_lsb: _lvgl._Bool) -> None:
    return _lvgl.draw_sw_i1_convert_to_vtiled(buf, buf_size, width, height, out_buf, out_buf_size, bit_order_lsb)


def draw_sw_rotate(src: None, dest: None, src_width: _lvgl.int32_t, src_height: _lvgl.int32_t, src_stride: _lvgl.int32_t, dest_stride: _lvgl.int32_t, rotation: _lvgl.display_rotation_t, color_format: _lvgl.color_format_t) -> None:
    return _lvgl.draw_sw_rotate(src, dest, src_width, src_height, src_stride, dest_stride, rotation, color_format)


def snapshot_take(obj: "obj", cf: _lvgl.color_format_t) -> "draw_buf_t":
    return _lvgl.snapshot_take(obj, cf)


def snapshot_create_draw_buf(obj: "obj", cf: _lvgl.color_format_t) -> "draw_buf_t":
    return _lvgl.snapshot_create_draw_buf(obj, cf)


def snapshot_reshape_draw_buf(obj: "obj", draw_buf: "draw_buf_t") -> _lvgl.result_t:
    return _lvgl.snapshot_reshape_draw_buf(obj, draw_buf)


def snapshot_take_to_draw_buf(obj: "obj", cf: _lvgl.color_format_t, draw_buf: "draw_buf_t") -> _lvgl.result_t:
    return _lvgl.snapshot_take_to_draw_buf(obj, cf, draw_buf)


def snapshot_free(dsc: "image_dsc_t") -> None:
    return _lvgl.snapshot_free(dsc)


def snapshot_take_to_buf(obj: "obj", cf: _lvgl.color_format_t, dsc: "image_dsc_t", buf: None, buf_size: _lvgl.uint32_t) -> _lvgl.result_t:
    return _lvgl.snapshot_take_to_buf(obj, cf, dsc, buf, buf_size)


def theme_get_from_obj(obj: "obj") -> "theme_t":
    return _lvgl.theme_get_from_obj(obj)


def theme_apply(obj: "obj") -> None:
    return _lvgl.theme_apply(obj)


def theme_get_font_small(obj: "obj") -> "font_t":
    return _lvgl.theme_get_font_small(obj)


def theme_get_font_normal(obj: "obj") -> "font_t":
    return _lvgl.theme_get_font_normal(obj)


def theme_get_font_large(obj: "obj") -> "font_t":
    return _lvgl.theme_get_font_large(obj)


def theme_get_color_primary(obj: "obj") -> "color_t":
    return _lvgl.theme_get_color_primary(obj)


def theme_get_color_secondary(obj: "obj") -> "color_t":
    return _lvgl.theme_get_color_secondary(obj)


def theme_default_init(disp: "display_t", color_primary: "color_t", color_secondary: "color_t", dark: _lvgl._Bool, font: "font_t") -> "theme_t":
    return _lvgl.theme_default_init(disp, color_primary, color_secondary, dark, font)


def theme_default_is_inited() -> _lvgl._Bool:
    return _lvgl.theme_default_is_inited()


def theme_default_get() -> "theme_t":
    return _lvgl.theme_default_get()


def theme_default_deinit() -> None:
    return _lvgl.theme_default_deinit()


def theme_simple_init(disp: "display_t") -> "theme_t":
    return _lvgl.theme_simple_init(disp)


def theme_simple_is_inited() -> _lvgl._Bool:
    return _lvgl.theme_simple_is_inited()


def theme_simple_get() -> "theme_t":
    return _lvgl.theme_simple_get()


def theme_simple_deinit() -> None:
    return _lvgl.theme_simple_deinit()


def sdl_window_create(hor_res: _lvgl.int32_t, ver_res: _lvgl.int32_t) -> "display_t":
    return _lvgl.sdl_window_create(hor_res, ver_res)


def sdl_window_set_resizeable(disp: "display_t", value: _lvgl._Bool) -> None:
    return _lvgl.sdl_window_set_resizeable(disp, value)


def sdl_window_set_size(disp: "display_t", hor_res: _lvgl.int32_t, ver_res: _lvgl.int32_t) -> None:
    return _lvgl.sdl_window_set_size(disp, hor_res, ver_res)


def sdl_window_set_zoom(disp: "display_t", zoom: "Float") -> None:
    return _lvgl.sdl_window_set_zoom(disp, zoom)


def sdl_window_get_zoom(disp: "display_t") -> "Float":
    return _lvgl.sdl_window_get_zoom(disp)


def sdl_window_set_title(disp: "display_t", title: _lvgl.char) -> None:
    return _lvgl.sdl_window_set_title(disp, title)


def sdl_window_set_icon(disp: "display_t", icon: None, width: _lvgl.int32_t, height: _lvgl.int32_t) -> None:
    return _lvgl.sdl_window_set_icon(disp, icon, width, height)


def sdl_window_get_renderer(disp: "display_t") -> "Any":
    return _lvgl.sdl_window_get_renderer(disp)


def sdl_quit() -> None:
    return _lvgl.sdl_quit()


def sdl_window_get_window(disp: "display_t") -> "SDL_Window":
    return _lvgl.sdl_window_get_window(disp)


def sdl_mouse_create() -> "indev_t":
    return _lvgl.sdl_mouse_create()


def sdl_mousewheel_create() -> "indev_t":
    return _lvgl.sdl_mousewheel_create()


def sdl_keyboard_create() -> "indev_t":
    return _lvgl.sdl_keyboard_create()


def task_handler() -> _lvgl.uint32_t:
    return _lvgl.task_handler()


def version_major() -> _lvgl.int_:
    return _lvgl.version_major()


def version_minor() -> _lvgl.int_:
    return _lvgl.version_minor()


def version_patch() -> _lvgl.int_:
    return _lvgl.version_patch()


def version_info() -> _lvgl.char:
    return _lvgl.version_info()


def demos_show_help() -> None:
    return _lvgl.demos_show_help()


def timer_create(timer_xcb: "timer_cb_t", period: _lvgl.uint32_t, user_data: "Any") -> "timer_t":
    return _lvgl.timer_create(timer_xcb, period, user_data)


def anim_timeline_create() -> "anim_timeline_t":
    return _lvgl.anim_timeline_create()


def draw_buf_create(w: _lvgl.uint32_t, h: _lvgl.uint32_t, cf: _lvgl.color_format_t, stride: _lvgl.uint32_t) -> "draw_buf_t":
    return _lvgl.draw_buf_create(w, h, cf, stride)


def iter_create(instance: None, elem_size: _lvgl.uint32_t, context_size: _lvgl.uint32_t, next_cb: "iter_next_cb") -> "iter_t":
    return _lvgl.iter_create(instance, elem_size, context_size, next_cb)


def circle_buf_create(capacity: _lvgl.uint32_t, element_size: _lvgl.uint32_t) -> "circle_buf_t":
    return _lvgl.circle_buf_create(capacity, element_size)


def display_create(hor_res: _lvgl.int32_t, ver_res: _lvgl.int32_t) -> "display_t":
    return _lvgl.display_create(hor_res, ver_res)


def image_decoder_create() -> "image_decoder_t":
    return _lvgl.image_decoder_create()


def group_create() -> "group_t":
    return _lvgl.group_create()


def binfont_create(path: _lvgl.char) -> "font_t":
    return _lvgl.binfont_create(path)


def imgfont_create(height: _lvgl.uint16_t, path_cb: "imgfont_get_path_cb_t", user_data: "Any") -> "font_t":
    return _lvgl.imgfont_create(height, path_cb, user_data)


def theme_create() -> "theme_t":
    return _lvgl.theme_create()


def demos_create(info: "List", size: _lvgl.int_) -> _lvgl._Bool:
    return _lvgl.demos_create(info, size)



class draw_task_t(_lvgl.draw_task_t):

    def image_core_cb(self, draw_dsc: "draw_image_dsc_t", decoder_dsc: "image_decoder_dsc_t", sup: "draw_image_sup_t", img_coords: "area_t", clipped_img_area: "area_t") -> None:
        return _lvgl.draw_image_core_cb(self, draw_dsc, decoder_dsc, sup, img_coords, clipped_img_area)

    def get_dependent_count(self) -> _lvgl.uint32_t:
        return _lvgl.draw_get_dependent_count(self)

    def get_type(self) -> _lvgl.draw_task_type_t:
        return _lvgl.draw_task_get_type(self)

    def get_draw_dsc(self) -> "Any":
        return _lvgl.draw_task_get_draw_dsc(self)

    def get_area(self, area: "area_t") -> None:
        return _lvgl.draw_task_get_area(self, area)

    def get_fill_dsc(self) -> "draw_fill_dsc_t":
        return _lvgl.draw_task_get_fill_dsc(self)

    def get_border_dsc(self) -> "draw_border_dsc_t":
        return _lvgl.draw_task_get_border_dsc(self)

    def get_box_shadow_dsc(self) -> "draw_box_shadow_dsc_t":
        return _lvgl.draw_task_get_box_shadow_dsc(self)

    def get_label_dsc(self) -> "draw_label_dsc_t":
        return _lvgl.draw_task_get_label_dsc(self)

    def label_iterate_characters(self, dsc: "draw_label_dsc_t", coords: "area_t", cb: "draw_glyph_cb_t") -> None:
        return _lvgl.draw_label_iterate_characters(self, dsc, coords, cb)

    def unit_draw_letter(self, dsc: "draw_glyph_dsc_t", pos: _lvgl.point_t, font: "font_t", letter: _lvgl.uint32_t, cb: "draw_glyph_cb_t") -> None:
        return _lvgl.draw_unit_draw_letter(self, dsc, pos, font, letter, cb)

    def get_image_dsc(self) -> "draw_image_dsc_t":
        return _lvgl.draw_task_get_image_dsc(self)

    def get_line_dsc(self) -> "draw_line_dsc_t":
        return _lvgl.draw_task_get_line_dsc(self)

    def line_iterate(self, dsc: "draw_line_dsc_t", draw_line_cb: _lvgl.void) -> None:
        return _lvgl.draw_line_iterate(self, dsc, draw_line_cb)

    def get_arc_dsc(self) -> "draw_arc_dsc_t":
        return _lvgl.draw_task_get_arc_dsc(self)

    def get_triangle_dsc(self) -> "draw_triangle_dsc_t":
        return _lvgl.draw_task_get_triangle_dsc(self)

    def get_blur_dsc(self) -> "draw_blur_dsc_t":
        return _lvgl.draw_task_get_blur_dsc(self)


class mem_monitor_t(_lvgl.mem_monitor_t):

    def core(self) -> None:
        return _lvgl.mem_monitor_core(self)

    def mem_monitor(self) -> None:
        return _lvgl.mem_monitor(self)


class ll_t(_lvgl.ll_t):

    def init(self, node_size: _lvgl.uint32_t) -> None:
        return _lvgl.ll_init(self, node_size)

    def ins_head(self) -> "Any":
        return _lvgl.ll_ins_head(self)

    def ins_prev(self, n_act: _lvgl.void) -> "Any":
        return _lvgl.ll_ins_prev(self, n_act)

    def ins_tail(self) -> "Any":
        return _lvgl.ll_ins_tail(self)

    def remove(self, node_p: _lvgl.void) -> None:
        return _lvgl.ll_remove(self, node_p)

    def clear_custom(self, cleanup: _lvgl.void) -> None:
        return _lvgl.ll_clear_custom(self, cleanup)

    def clear(self) -> None:
        return _lvgl.ll_clear(self)

    def chg_list(self, ll_new_p: "ll_t", node: _lvgl.void, head: _lvgl._Bool) -> None:
        return _lvgl.ll_chg_list(self, ll_new_p, node, head)

    def get_head(self) -> "Any":
        return _lvgl.ll_get_head(self)

    def get_tail(self) -> "Any":
        return _lvgl.ll_get_tail(self)

    def get_next(self, n_act: _lvgl.void) -> "Any":
        return _lvgl.ll_get_next(self, n_act)

    def get_prev(self, n_act: _lvgl.void) -> "Any":
        return _lvgl.ll_get_prev(self, n_act)

    def get_len(self) -> _lvgl.uint32_t:
        return _lvgl.ll_get_len(self)

    def move_before(self, n_act: _lvgl.void, n_after: _lvgl.void) -> None:
        return _lvgl.ll_move_before(self, n_act, n_after)

    def is_empty(self) -> _lvgl._Bool:
        return _lvgl.ll_is_empty(self)


class timer_t(_lvgl.timer_t):

    def delete(self) -> None:
        callback_ref = _callback_ref_from_user_data(
            _lvgl.timer_get_user_data(self)
        )
        result = _lvgl.timer_delete(self)
        _release_event_callback_ref(callback_ref)
        return result

    def pause(self) -> None:
        return _lvgl.timer_pause(self)

    def resume(self) -> None:
        return _lvgl.timer_resume(self)

    def set_cb(self, timer_cb: "timer_cb_t") -> None:
        return _lvgl.timer_set_cb(self, timer_cb)

    def set_period(self, period: _lvgl.uint32_t) -> None:
        return _lvgl.timer_set_period(self, period)

    def ready(self) -> None:
        return _lvgl.timer_ready(self)

    def set_repeat_count(self, repeat_count: _lvgl.int32_t) -> None:
        return _lvgl.timer_set_repeat_count(self, repeat_count)

    def set_auto_delete(self, auto_delete: _lvgl._Bool) -> None:
        return _lvgl.timer_set_auto_delete(self, auto_delete)

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.timer_set_user_data(self, user_data)

    def reset(self) -> None:
        return _lvgl.timer_reset(self)

    def get_next(self) -> "timer_t":
        return _lvgl.timer_get_next(self)

    def get_user_data(self) -> "Any":
        return _lvgl.timer_get_user_data(self)

    def get_paused(self) -> _lvgl._Bool:
        return _lvgl.timer_get_paused(self)


class array_t(_lvgl.array_t):

    def init(self, capacity: _lvgl.uint32_t, element_size: _lvgl.uint32_t) -> None:
        return _lvgl.array_init(self, capacity, element_size)

    def init_from_buf(self, buf: _lvgl.void, capacity: _lvgl.uint32_t, element_size: _lvgl.uint32_t) -> None:
        return _lvgl.array_init_from_buf(self, buf, capacity, element_size)

    def resize(self, new_capacity: _lvgl.uint32_t) -> _lvgl._Bool:
        return _lvgl.array_resize(self, new_capacity)

    def deinit(self) -> None:
        return _lvgl.array_deinit(self)

    def size(self) -> _lvgl.uint32_t:
        return _lvgl.array_size(self)

    def capacity(self) -> _lvgl.uint32_t:
        return _lvgl.array_capacity(self)

    def is_empty(self) -> _lvgl._Bool:
        return _lvgl.array_is_empty(self)

    def is_full(self) -> _lvgl._Bool:
        return _lvgl.array_is_full(self)

    def copy(self, source: "array_t") -> None:
        return _lvgl.array_copy(self, source)

    def clear(self) -> None:
        return _lvgl.array_clear(self)

    def shrink(self) -> None:
        return _lvgl.array_shrink(self)

    def remove(self, index: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.array_remove(self, index)

    def remove_unordered(self, index: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.array_remove_unordered(self, index)

    def erase(self, start: _lvgl.uint32_t, end: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.array_erase(self, start, end)

    def concat(self, other: "array_t") -> _lvgl.result_t:
        return _lvgl.array_concat(self, other)

    def push_back(self, element: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.array_push_back(self, element)

    def assign(self, index: _lvgl.uint32_t, value: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.array_assign(self, index, value)

    def at(self, index: _lvgl.uint32_t) -> "Any":
        return _lvgl.array_at(self, index)

    def front(self) -> "Any":
        return _lvgl.array_front(self)

    def back(self) -> "Any":
        return _lvgl.array_back(self)


class anim_t(_lvgl.anim_t):

    def init(self) -> None:
        return _lvgl.anim_init(self)

    def set_var(self, var: _lvgl.void) -> None:
        return _lvgl.anim_set_var(self, var)

    def set_exec_cb(self, exec_cb: "anim_exec_xcb_t") -> None:
        return _lvgl.anim_set_exec_cb(self, exec_cb)

    def set_duration(self, duration: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_duration(self, duration)

    def set_delay(self, delay: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_delay(self, delay)

    def resume(self) -> None:
        return _lvgl.anim_resume(self)

    def pause(self) -> None:
        return _lvgl.anim_pause(self)

    def pause_for(self, ms: _lvgl.uint32_t) -> None:
        return _lvgl.anim_pause_for(self, ms)

    def is_paused(self) -> _lvgl._Bool:
        return _lvgl.anim_is_paused(self)

    def set_values(self, start: _lvgl.int32_t, end: _lvgl.int32_t) -> None:
        return _lvgl.anim_set_values(self, start, end)

    def set_custom_exec_cb(self, exec_cb: "anim_custom_exec_cb_t") -> None:
        return _lvgl.anim_set_custom_exec_cb(self, exec_cb)

    def set_path_cb(self, path_cb: "anim_path_cb_t") -> None:
        return _lvgl.anim_set_path_cb(self, path_cb)

    def set_start_cb(self, start_cb: "anim_start_cb_t") -> None:
        return _lvgl.anim_set_start_cb(self, start_cb)

    def set_get_value_cb(self, get_value_cb: "anim_get_value_cb_t") -> None:
        return _lvgl.anim_set_get_value_cb(self, get_value_cb)

    def set_completed_cb(self, completed_cb: "anim_completed_cb_t") -> None:
        return _lvgl.anim_set_completed_cb(self, completed_cb)

    def set_deleted_cb(self, deleted_cb: "anim_deleted_cb_t") -> None:
        return _lvgl.anim_set_deleted_cb(self, deleted_cb)

    def set_reverse_duration(self, duration: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_reverse_duration(self, duration)

    def set_reverse_time(self, duration: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_reverse_time(self, duration)

    def set_reverse_delay(self, delay: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_reverse_delay(self, delay)

    def set_repeat_count(self, cnt: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_repeat_count(self, cnt)

    def set_repeat_delay(self, delay: _lvgl.uint32_t) -> None:
        return _lvgl.anim_set_repeat_delay(self, delay)

    def set_early_apply(self, en: _lvgl._Bool) -> None:
        return _lvgl.anim_set_early_apply(self, en)

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.anim_set_user_data(self, user_data)

    def set_bezier3_param(self, x1: _lvgl.int16_t, y1: _lvgl.int16_t, x2: _lvgl.int16_t, y2: _lvgl.int16_t) -> None:
        return _lvgl.anim_set_bezier3_param(self, x1, y1, x2, y2)

    def start(self) -> "anim_t":
        return _lvgl.anim_start(self)

    def get_delay(self) -> _lvgl.uint32_t:
        return _lvgl.anim_get_delay(self)

    def get_playtime(self) -> _lvgl.uint32_t:
        return _lvgl.anim_get_playtime(self)

    def get_time(self) -> _lvgl.uint32_t:
        return _lvgl.anim_get_time(self)

    def get_repeat_count(self) -> _lvgl.uint32_t:
        return _lvgl.anim_get_repeat_count(self)

    def get_user_data(self) -> "Any":
        return _lvgl.anim_get_user_data(self)

    def custom_delete(self, exec_cb: "anim_custom_exec_cb_t") -> _lvgl._Bool:
        return _lvgl.anim_custom_delete(self, exec_cb)

    def custom_get(self, exec_cb: "anim_custom_exec_cb_t") -> "anim_t":
        return _lvgl.anim_custom_get(self, exec_cb)


class anim_timeline_t(_lvgl.anim_timeline_t):

    def delete(self) -> None:
        return _lvgl.anim_timeline_delete(self)

    def add(self, start_time: _lvgl.uint32_t, a: "anim_t") -> None:
        return _lvgl.anim_timeline_add(self, start_time, a)

    def start(self) -> _lvgl.uint32_t:
        return _lvgl.anim_timeline_start(self)

    def pause(self) -> None:
        return _lvgl.anim_timeline_pause(self)

    def set_reverse(self, reverse: _lvgl._Bool) -> None:
        return _lvgl.anim_timeline_set_reverse(self, reverse)

    def set_delay(self, delay: _lvgl.uint32_t) -> None:
        return _lvgl.anim_timeline_set_delay(self, delay)

    def set_repeat_count(self, cnt: _lvgl.uint32_t) -> None:
        return _lvgl.anim_timeline_set_repeat_count(self, cnt)

    def set_repeat_delay(self, delay: _lvgl.uint32_t) -> None:
        return _lvgl.anim_timeline_set_repeat_delay(self, delay)

    def set_progress(self, progress: _lvgl.uint16_t) -> None:
        return _lvgl.anim_timeline_set_progress(self, progress)

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.anim_timeline_set_user_data(self, user_data)

    def get_playtime(self) -> _lvgl.uint32_t:
        return _lvgl.anim_timeline_get_playtime(self)

    def get_reverse(self) -> _lvgl._Bool:
        return _lvgl.anim_timeline_get_reverse(self)

    def get_delay(self) -> _lvgl.uint32_t:
        return _lvgl.anim_timeline_get_delay(self)

    def get_progress(self) -> _lvgl.uint16_t:
        return _lvgl.anim_timeline_get_progress(self)

    def get_repeat_count(self) -> _lvgl.uint32_t:
        return _lvgl.anim_timeline_get_repeat_count(self)

    def get_repeat_delay(self) -> _lvgl.uint32_t:
        return _lvgl.anim_timeline_get_repeat_delay(self)

    def get_user_data(self) -> "Any":
        return _lvgl.anim_timeline_get_user_data(self)

    def merge(self, src: "anim_timeline_t", delay: _lvgl.int32_t) -> None:
        return _lvgl.anim_timeline_merge(self, src, delay)


class rb_t(_lvgl.rb_t):

    def init(self, compare: "rb_compare_t", node_size: _lvgl.size_t) -> _lvgl._Bool:
        return _lvgl.rb_init(self, compare, node_size)

    def insert(self, key: _lvgl.void) -> "rb_node_t":
        return _lvgl.rb_insert(self, key)

    def find(self, key: _lvgl.void) -> "rb_node_t":
        return _lvgl.rb_find(self, key)

    def remove_node(self, node: "rb_node_t") -> "Any":
        return _lvgl.rb_remove_node(self, node)

    def remove(self, key: _lvgl.void) -> "Any":
        return _lvgl.rb_remove(self, key)

    def drop_node(self, node: "rb_node_t") -> _lvgl._Bool:
        return _lvgl.rb_drop_node(self, node)

    def drop(self, key: _lvgl.void) -> _lvgl._Bool:
        return _lvgl.rb_drop(self, key)

    def minimum(self) -> "rb_node_t":
        return _lvgl.rb_minimum(self)

    def maximum(self) -> "rb_node_t":
        return _lvgl.rb_maximum(self)

    def destroy(self) -> None:
        return _lvgl.rb_destroy(self)


class rb_node_t(_lvgl.rb_node_t):

    def minimum_from(self) -> "rb_node_t":
        return _lvgl.rb_minimum_from(self)

    def maximum_from(self) -> "rb_node_t":
        return _lvgl.rb_maximum_from(self)


class area_t(_lvgl.area_t):

    def set(self, x1: _lvgl.int32_t, y1: _lvgl.int32_t, x2: _lvgl.int32_t, y2: _lvgl.int32_t) -> None:
        return _lvgl.area_set(self, x1, y1, x2, y2)

    def copy(self, src: "area_t") -> None:
        return _lvgl.area_copy(self, src)

    def get_width(self) -> _lvgl.int32_t:
        return _lvgl.area_get_width(self)

    def get_height(self) -> _lvgl.int32_t:
        return _lvgl.area_get_height(self)

    def set_width(self, w: _lvgl.int32_t) -> None:
        return _lvgl.area_set_width(self, w)

    def set_height(self, h: _lvgl.int32_t) -> None:
        return _lvgl.area_set_height(self, h)

    def get_size(self) -> _lvgl.uint32_t:
        return _lvgl.area_get_size(self)

    def increase(self, w_extra: _lvgl.int32_t, h_extra: _lvgl.int32_t) -> None:
        return _lvgl.area_increase(self, w_extra, h_extra)

    def move(self, x_ofs: _lvgl.int32_t, y_ofs: _lvgl.int32_t) -> None:
        return _lvgl.area_move(self, x_ofs, y_ofs)

    def align(self, to_align: "area_t", align: _lvgl.align_t, ofs_x: _lvgl.int32_t, ofs_y: _lvgl.int32_t) -> None:
        return _lvgl.area_align(self, to_align, align, ofs_x, ofs_y)


class point_t(_lvgl.point_t):

    def transform(self, angle: _lvgl.int32_t, scale_x: _lvgl.int32_t, scale_y: _lvgl.int32_t, pivot: _lvgl.point_t, zoom_first: _lvgl._Bool) -> None:
        return _lvgl.point_transform(self, angle, scale_x, scale_y, pivot, zoom_first)

    def array_transform(self, count: _lvgl.size_t, angle: _lvgl.int32_t, scale_x: _lvgl.int32_t, scale_y: _lvgl.int32_t, pivot: _lvgl.point_t, zoom_first: _lvgl._Bool) -> None:
        return _lvgl.point_array_transform(self, count, angle, scale_x, scale_y, pivot, zoom_first)

    def to_precise(self) -> _lvgl.point_precise_t:
        return _lvgl.point_to_precise(self)

    def set(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> None:
        return _lvgl.point_set(self, x, y)

    def swap(self, p2: _lvgl.point_t) -> None:
        return _lvgl.point_swap(self, p2)


class point_precise_t(_lvgl.point_precise_t):

    def from_precise(self) -> _lvgl.point_t:
        return _lvgl.point_from_precise(self)

    def set(self, x: _lvgl.value_precise_t, y: _lvgl.value_precise_t) -> None:
        return _lvgl.point_precise_set(self, x, y)

    def swap(self, p2: _lvgl.point_precise_t) -> None:
        return _lvgl.point_precise_swap(self, p2)


class color_t(_lvgl.color_t):

    def to_32(self, opa: _lvgl.opa_t) -> "color32_t":
        return _lvgl.color_to_32(self, opa)

    def to_int(self) -> _lvgl.uint32_t:
        return _lvgl.color_to_int(self)

    def eq(self, c2: "color_t") -> _lvgl._Bool:
        return _lvgl.color_eq(self, c2)

    def is_in_range(self, l_color: "color_t", h_color: "color_t") -> _lvgl._Bool:
        return _lvgl.color_is_in_range(self, l_color, h_color)

    def to_u16(self) -> _lvgl.uint16_t:
        return _lvgl.color_to_u16(self)

    def to_u32(self) -> _lvgl.uint32_t:
        return _lvgl.color_to_u32(self)

    def lighten(self, lvl: _lvgl.opa_t) -> "color_t":
        return _lvgl.color_lighten(self, lvl)

    def darken(self, lvl: _lvgl.opa_t) -> "color_t":
        return _lvgl.color_darken(self, lvl)

    def to_hsv(self) -> "color_hsv_t":
        return _lvgl.color_to_hsv(self)

    def luminance(self) -> _lvgl.uint8_t:
        return _lvgl.color_luminance(self)

    def mix(self, c2: "color_t", mix: _lvgl.uint8_t) -> "color_t":
        return _lvgl.color_mix(self, c2, mix)

    def brightness(self) -> _lvgl.uint8_t:
        return _lvgl.color_brightness(self)


class color32_t(_lvgl.color32_t):

    def eq(self, c2: "color32_t") -> _lvgl._Bool:
        return _lvgl.color32_eq(self, c2)

    def luminance(self) -> _lvgl.uint8_t:
        return _lvgl.color32_luminance(self)


class color16_t(_lvgl.color16_t):

    def to_color(self) -> "color_t":
        return _lvgl.color16_to_color(self)

    def premultiply(self, a: _lvgl.opa_t) -> None:
        return _lvgl.color16_premultiply(self, a)

    def luminance(self) -> _lvgl.uint8_t:
        return _lvgl.color16_luminance(self)


class color_filter_dsc_t(_lvgl.color_filter_dsc_t):

    def init(self, cb: "color_filter_cb_t") -> None:
        return _lvgl.color_filter_dsc_init(self, cb)


class draw_buf_handlers_t(_lvgl.draw_buf_handlers_t):

    def init_with_default_handlers(self) -> None:
        return _lvgl.draw_buf_init_with_default_handlers(self)

    def init(self, buf_malloc_cb: "draw_buf_malloc_cb_t", buf_free_cb: "draw_buf_free_cb_t", buf_copy_cb: "draw_buf_copy_cb_t", align_pointer_cb: "draw_buf_align_cb_t", invalidate_cache_cb: "draw_buf_cache_operation_cb_t", flush_cache_cb: "draw_buf_cache_operation_cb_t", width_to_stride_cb: "draw_buf_width_to_stride_cb_t") -> None:
        return _lvgl.draw_buf_handlers_init(self, buf_malloc_cb, buf_free_cb, buf_copy_cb, align_pointer_cb, invalidate_cache_cb, flush_cache_cb, width_to_stride_cb)

    def align_ex(self, buf: _lvgl.void, color_format: _lvgl.color_format_t) -> "Any":
        return _lvgl.draw_buf_align_ex(self, buf, color_format)

    def width_to_stride_ex(self, w: _lvgl.uint32_t, color_format: _lvgl.color_format_t) -> _lvgl.uint32_t:
        return _lvgl.draw_buf_width_to_stride_ex(self, w, color_format)

    def create_ex(self, w: _lvgl.uint32_t, h: _lvgl.uint32_t, cf: _lvgl.color_format_t, stride: _lvgl.uint32_t) -> "draw_buf_t":
        return _lvgl.draw_buf_create_ex(self, w, h, cf, stride)

    def dup_ex(self, draw_buf: "draw_buf_t") -> "draw_buf_t":
        return _lvgl.draw_buf_dup_ex(self, draw_buf)


class draw_buf_t(_lvgl.draw_buf_t):

    def invalidate_cache(self, area: "area_t") -> None:
        return _lvgl.draw_buf_invalidate_cache(self, area)

    def flush_cache(self, area: "area_t") -> None:
        return _lvgl.draw_buf_flush_cache(self, area)

    def clear(self, a: "area_t") -> None:
        return _lvgl.draw_buf_clear(self, a)

    def dup(self) -> "draw_buf_t":
        return _lvgl.draw_buf_dup(self)

    def init(self, w: _lvgl.uint32_t, h: _lvgl.uint32_t, cf: _lvgl.color_format_t, stride: _lvgl.uint32_t, data: _lvgl.void, data_size: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.draw_buf_init(self, w, h, cf, stride, data, data_size)

    def reshape(self, cf: _lvgl.color_format_t, w: _lvgl.uint32_t, h: _lvgl.uint32_t, stride: _lvgl.uint32_t) -> "draw_buf_t":
        return _lvgl.draw_buf_reshape(self, cf, w, h, stride)

    def destroy(self) -> None:
        return _lvgl.draw_buf_destroy(self)

    def copy(self, dest_area: "area_t", src: "draw_buf_t", src_area: "area_t") -> None:
        return _lvgl.draw_buf_copy(self, dest_area, src, src_area)

    def goto_xy(self, x: _lvgl.uint32_t, y: _lvgl.uint32_t) -> "Any":
        return _lvgl.draw_buf_goto_xy(self, x, y)

    def adjust_stride(self, stride: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.draw_buf_adjust_stride(self, stride)

    def premultiply(self) -> _lvgl.result_t:
        return _lvgl.draw_buf_premultiply(self)

    def has_flag(self, flag: _lvgl.image_flags_t) -> _lvgl._Bool:
        return _lvgl.draw_buf_has_flag(self, flag)

    def set_flag(self, flag: _lvgl.image_flags_t) -> None:
        return _lvgl.draw_buf_set_flag(self, flag)

    def clear_flag(self, flag: _lvgl.image_flags_t) -> None:
        return _lvgl.draw_buf_clear_flag(self, flag)

    def from_image(self, img: "image_dsc_t") -> _lvgl.result_t:
        return _lvgl.draw_buf_from_image(self, img)

    def to_image(self, img: "image_dsc_t") -> None:
        return _lvgl.draw_buf_to_image(self, img)

    def set_palette(self, index: _lvgl.uint8_t, color: "color32_t") -> None:
        return _lvgl.draw_buf_set_palette(self, index, color)

    def save_to_file(self, path: _lvgl.char) -> _lvgl.result_t:
        return _lvgl.draw_buf_save_to_file(self, path)


class image_dsc_t(_lvgl.image_dsc_t):

    def buf_set_palette(self, id: _lvgl.uint8_t, c: "color32_t") -> None:
        return _lvgl.image_buf_set_palette(self, id, c)

    def buf_free(self) -> None:
        return _lvgl.image_buf_free(self)


class iter_t(_lvgl.iter_t):

    def get_context(self) -> "Any":
        return _lvgl.iter_get_context(self)

    def destroy(self) -> None:
        return _lvgl.iter_destroy(self)

    def next(self, elem: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.iter_next(self, elem)

    def make_peekable(self, capacity: _lvgl.uint32_t) -> None:
        return _lvgl.iter_make_peekable(self, capacity)

    def peek(self, elem: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.iter_peek(self, elem)

    def peek_advance(self) -> _lvgl.result_t:
        return _lvgl.iter_peek_advance(self)

    def peek_reset(self) -> _lvgl.result_t:
        return _lvgl.iter_peek_reset(self)

    def inspect(self, inspect_cb: "iter_inspect_cb") -> None:
        return _lvgl.iter_inspect(self, inspect_cb)


class circle_buf_t(_lvgl.circle_buf_t):

    def resize(self, capacity: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.circle_buf_resize(self, capacity)

    def destroy(self) -> None:
        return _lvgl.circle_buf_destroy(self)

    def size(self) -> _lvgl.uint32_t:
        return _lvgl.circle_buf_size(self)

    def capacity(self) -> _lvgl.uint32_t:
        return _lvgl.circle_buf_capacity(self)

    def remain(self) -> _lvgl.uint32_t:
        return _lvgl.circle_buf_remain(self)

    def is_empty(self) -> _lvgl._Bool:
        return _lvgl.circle_buf_is_empty(self)

    def is_full(self) -> _lvgl._Bool:
        return _lvgl.circle_buf_is_full(self)

    def reset(self) -> None:
        return _lvgl.circle_buf_reset(self)

    def head(self) -> "Any":
        return _lvgl.circle_buf_head(self)

    def tail(self) -> "Any":
        return _lvgl.circle_buf_tail(self)

    def read(self, data: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.circle_buf_read(self, data)

    def write(self, data: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.circle_buf_write(self, data)

    def fill(self, count: _lvgl.uint32_t, fill_cb: "circle_buf_fill_cb_t", user_data: "Any") -> _lvgl.uint32_t:
        return _lvgl.circle_buf_fill(self, count, fill_cb, user_data)

    def skip(self) -> _lvgl.result_t:
        return _lvgl.circle_buf_skip(self)

    def peek(self, data: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.circle_buf_peek(self, data)

    def peek_at(self, index: _lvgl.uint32_t, data: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.circle_buf_peek_at(self, index, data)


class tree_node_t(_lvgl.tree_node_t):

    def delete(self) -> None:
        return _lvgl.tree_node_delete(self)

    def walk(self, mode: _lvgl.tree_walk_mode_t, cb: "tree_traverse_cb_t", bcb: "tree_before_cb_t", acb: "tree_after_cb_t", user_data: "Any") -> _lvgl._Bool:
        return _lvgl.tree_walk(self, mode, cb, bcb, acb, user_data)


class font_glyph_dsc_t(_lvgl.font_glyph_dsc_t):

    def get_glyph_bitmap(self, draw_buf: "draw_buf_t") -> "Any":
        return _lvgl.font_get_glyph_bitmap(self, draw_buf)

    def get_glyph_static_bitmap(self) -> "Any":
        return _lvgl.font_get_glyph_static_bitmap(self)

    def release_draw_data(self) -> None:
        return _lvgl.font_glyph_release_draw_data(self)

    def get_bitmap_fmt_txt(self, draw_buf: "draw_buf_t") -> "Any":
        return _lvgl.font_get_bitmap_fmt_txt(self, draw_buf)


class font_t(_lvgl.font_t):

    def get_glyph_dsc(self, dsc_out: "font_glyph_dsc_t", letter: _lvgl.uint32_t, letter_next: _lvgl.uint32_t) -> _lvgl._Bool:
        return _lvgl.font_get_glyph_dsc(self, dsc_out, letter, letter_next)

    def get_glyph_width(self, letter: _lvgl.uint32_t, letter_next: _lvgl.uint32_t) -> _lvgl.uint16_t:
        return _lvgl.font_get_glyph_width(self, letter, letter_next)

    def get_line_height(self) -> _lvgl.int32_t:
        return _lvgl.font_get_line_height(self)

    def set_kerning(self, kerning: _lvgl.font_kerning_t) -> None:
        return _lvgl.font_set_kerning(self, kerning)

    def has_static_bitmap(self) -> _lvgl._Bool:
        return _lvgl.font_has_static_bitmap(self)

    def get_glyph_dsc_fmt_txt(self, dsc_out: "font_glyph_dsc_t", unicode_letter: _lvgl.uint32_t, unicode_letter_next: _lvgl.uint32_t) -> _lvgl._Bool:
        return _lvgl.font_get_glyph_dsc_fmt_txt(self, dsc_out, unicode_letter, unicode_letter_next)


class font_info_t(_lvgl.font_info_t):

    def is_equal(self, ft_info_2: "font_info_t") -> _lvgl._Bool:
        return _lvgl.font_info_is_equal(self, ft_info_2)


class grad_dsc_t(_lvgl.grad_dsc_t):

    def init_stops(self, colors: "List", opa: "List", fracs: "List", num_stops: _lvgl.int_) -> None:
        return _lvgl.grad_init_stops(self, colors, opa, fracs, num_stops)

    def horizontal_init(self) -> None:
        return _lvgl.grad_horizontal_init(self)

    def vertical_init(self) -> None:
        return _lvgl.grad_vertical_init(self)

    def linear_init(self, from_x: _lvgl.int32_t, from_y: _lvgl.int32_t, to_x: _lvgl.int32_t, to_y: _lvgl.int32_t, extend: _lvgl.grad_extend_t) -> None:
        return _lvgl.grad_linear_init(self, from_x, from_y, to_x, to_y, extend)

    def radial_init(self, center_x: _lvgl.int32_t, center_y: _lvgl.int32_t, to_x: _lvgl.int32_t, to_y: _lvgl.int32_t, extend: _lvgl.grad_extend_t) -> None:
        return _lvgl.grad_radial_init(self, center_x, center_y, to_x, to_y, extend)

    def radial_set_focal(self, center_x: _lvgl.int32_t, center_y: _lvgl.int32_t, radius: _lvgl.int32_t) -> None:
        return _lvgl.grad_radial_set_focal(self, center_x, center_y, radius)

    def conical_init(self, center_x: _lvgl.int32_t, center_y: _lvgl.int32_t, start_angle: _lvgl.int32_t, end_angle: _lvgl.int32_t, extend: _lvgl.grad_extend_t) -> None:
        return _lvgl.grad_conical_init(self, center_x, center_y, start_angle, end_angle, extend)


class style_t(_lvgl.style_t):

    def init(self) -> None:
        return _lvgl.style_init(self)

    def reset(self) -> None:
        return _lvgl.style_reset(self)

    def copy(self, src: "style_t") -> None:
        return _lvgl.style_copy(self, src)

    def merge(self, src: "style_t") -> None:
        return _lvgl.style_merge(self, src)

    def is_const(self) -> _lvgl._Bool:
        return _lvgl.style_is_const(self)

    def remove_prop(self, prop: _lvgl.style_prop_t) -> _lvgl._Bool:
        return _lvgl.style_remove_prop(self, prop)

    def set_prop(self, prop: _lvgl.style_prop_t, value: "style_value_t") -> None:
        return _lvgl.style_set_prop(self, prop, value)

    def get_prop(self, prop: _lvgl.style_prop_t, value: "style_value_t") -> _lvgl.style_res_t:
        return _lvgl.style_get_prop(self, prop, value)

    def get_prop_inlined(self, prop: _lvgl.style_prop_t, value: "style_value_t") -> _lvgl.style_res_t:
        return _lvgl.style_get_prop_inlined(self, prop, value)

    def is_empty(self) -> _lvgl._Bool:
        return _lvgl.style_is_empty(self)

    def set_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_width(self, value)

    def set_min_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_min_width(self, value)

    def set_max_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_max_width(self, value)

    def set_height(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_height(self, value)

    def set_min_height(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_min_height(self, value)

    def set_max_height(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_max_height(self, value)

    def set_length(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_length(self, value)

    def set_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_x(self, value)

    def set_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_y(self, value)

    def set_align(self, value: _lvgl.align_t) -> None:
        return _lvgl.style_set_align(self, value)

    def set_transform_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_width(self, value)

    def set_transform_height(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_height(self, value)

    def set_translate_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_translate_x(self, value)

    def set_translate_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_translate_y(self, value)

    def set_translate_radial(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_translate_radial(self, value)

    def set_transform_scale_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_scale_x(self, value)

    def set_transform_scale_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_scale_y(self, value)

    def set_transform_rotation(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_rotation(self, value)

    def set_transform_pivot_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_pivot_x(self, value)

    def set_transform_pivot_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_pivot_y(self, value)

    def set_transform_skew_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_skew_x(self, value)

    def set_transform_skew_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_skew_y(self, value)

    def set_pad_top(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_top(self, value)

    def set_pad_bottom(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_bottom(self, value)

    def set_pad_left(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_left(self, value)

    def set_pad_right(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_right(self, value)

    def set_pad_row(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_row(self, value)

    def set_pad_column(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_column(self, value)

    def set_pad_radial(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_radial(self, value)

    def set_margin_top(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_top(self, value)

    def set_margin_bottom(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_bottom(self, value)

    def set_margin_left(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_left(self, value)

    def set_margin_right(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_right(self, value)

    def set_bg_color(self, value: "color_t") -> None:
        return _lvgl.style_set_bg_color(self, value)

    def set_bg_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_bg_opa(self, value)

    def set_bg_grad_color(self, value: "color_t") -> None:
        return _lvgl.style_set_bg_grad_color(self, value)

    def set_bg_grad_dir(self, value: _lvgl.grad_dir_t) -> None:
        return _lvgl.style_set_bg_grad_dir(self, value)

    def set_bg_main_stop(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_bg_main_stop(self, value)

    def set_bg_grad_stop(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_bg_grad_stop(self, value)

    def set_bg_main_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_bg_main_opa(self, value)

    def set_bg_grad_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_bg_grad_opa(self, value)

    def set_bg_grad(self, value: "grad_dsc_t") -> None:
        return _lvgl.style_set_bg_grad(self, value)

    def set_bg_image_src(self, value: _lvgl.void) -> None:
        return _lvgl.style_set_bg_image_src(self, value)

    def set_bg_image_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_bg_image_opa(self, value)

    def set_bg_image_recolor(self, value: "color_t") -> None:
        return _lvgl.style_set_bg_image_recolor(self, value)

    def set_bg_image_recolor_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_bg_image_recolor_opa(self, value)

    def set_bg_image_tiled(self, value: _lvgl._Bool) -> None:
        return _lvgl.style_set_bg_image_tiled(self, value)

    def set_border_color(self, value: "color_t") -> None:
        return _lvgl.style_set_border_color(self, value)

    def set_border_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_border_opa(self, value)

    def set_border_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_border_width(self, value)

    def set_border_side(self, value: _lvgl.border_side_t) -> None:
        return _lvgl.style_set_border_side(self, value)

    def set_border_post(self, value: _lvgl._Bool) -> None:
        return _lvgl.style_set_border_post(self, value)

    def set_outline_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_outline_width(self, value)

    def set_outline_color(self, value: "color_t") -> None:
        return _lvgl.style_set_outline_color(self, value)

    def set_outline_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_outline_opa(self, value)

    def set_outline_pad(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_outline_pad(self, value)

    def set_shadow_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_shadow_width(self, value)

    def set_shadow_offset_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_shadow_offset_x(self, value)

    def set_shadow_offset_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_shadow_offset_y(self, value)

    def set_shadow_spread(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_shadow_spread(self, value)

    def set_shadow_color(self, value: "color_t") -> None:
        return _lvgl.style_set_shadow_color(self, value)

    def set_shadow_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_shadow_opa(self, value)

    def set_image_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_image_opa(self, value)

    def set_image_recolor(self, value: "color_t") -> None:
        return _lvgl.style_set_image_recolor(self, value)

    def set_image_recolor_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_image_recolor_opa(self, value)

    def set_image_colorkey(self, value: _lvgl.image_colorkey_t) -> None:
        return _lvgl.style_set_image_colorkey(self, value)

    def set_line_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_line_width(self, value)

    def set_line_dash_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_line_dash_width(self, value)

    def set_line_dash_gap(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_line_dash_gap(self, value)

    def set_line_rounded(self, value: _lvgl._Bool) -> None:
        return _lvgl.style_set_line_rounded(self, value)

    def set_line_color(self, value: "color_t") -> None:
        return _lvgl.style_set_line_color(self, value)

    def set_line_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_line_opa(self, value)

    def set_arc_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_arc_width(self, value)

    def set_arc_rounded(self, value: _lvgl._Bool) -> None:
        return _lvgl.style_set_arc_rounded(self, value)

    def set_arc_color(self, value: "color_t") -> None:
        return _lvgl.style_set_arc_color(self, value)

    def set_arc_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_arc_opa(self, value)

    def set_arc_image_src(self, value: _lvgl.void) -> None:
        return _lvgl.style_set_arc_image_src(self, value)

    def set_text_color(self, value: "color_t") -> None:
        return _lvgl.style_set_text_color(self, value)

    def set_text_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_text_opa(self, value)

    def set_text_font(self, value: "font_t") -> None:
        return _lvgl.style_set_text_font(self, value)

    def set_text_letter_space(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_text_letter_space(self, value)

    def set_text_line_space(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_text_line_space(self, value)

    def set_text_decor(self, value: _lvgl.text_decor_t) -> None:
        return _lvgl.style_set_text_decor(self, value)

    def set_text_align(self, value: _lvgl.text_align_t) -> None:
        return _lvgl.style_set_text_align(self, value)

    def set_text_outline_stroke_color(self, value: "color_t") -> None:
        return _lvgl.style_set_text_outline_stroke_color(self, value)

    def set_text_outline_stroke_width(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_text_outline_stroke_width(self, value)

    def set_text_outline_stroke_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_text_outline_stroke_opa(self, value)

    def set_blur_radius(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_blur_radius(self, value)

    def set_blur_backdrop(self, value: _lvgl._Bool) -> None:
        return _lvgl.style_set_blur_backdrop(self, value)

    def set_blur_quality(self, value: _lvgl.blur_quality_t) -> None:
        return _lvgl.style_set_blur_quality(self, value)

    def set_drop_shadow_radius(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_drop_shadow_radius(self, value)

    def set_drop_shadow_offset_x(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_drop_shadow_offset_x(self, value)

    def set_drop_shadow_offset_y(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_drop_shadow_offset_y(self, value)

    def set_drop_shadow_color(self, value: "color_t") -> None:
        return _lvgl.style_set_drop_shadow_color(self, value)

    def set_drop_shadow_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_drop_shadow_opa(self, value)

    def set_drop_shadow_quality(self, value: _lvgl.blur_quality_t) -> None:
        return _lvgl.style_set_drop_shadow_quality(self, value)

    def set_radius(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_radius(self, value)

    def set_radial_offset(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_radial_offset(self, value)

    def set_clip_corner(self, value: _lvgl._Bool) -> None:
        return _lvgl.style_set_clip_corner(self, value)

    def set_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_opa(self, value)

    def set_opa_layered(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_opa_layered(self, value)

    def set_color_filter_dsc(self, value: "color_filter_dsc_t") -> None:
        return _lvgl.style_set_color_filter_dsc(self, value)

    def set_color_filter_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_color_filter_opa(self, value)

    def set_recolor(self, value: "color_t") -> None:
        return _lvgl.style_set_recolor(self, value)

    def set_recolor_opa(self, value: _lvgl.opa_t) -> None:
        return _lvgl.style_set_recolor_opa(self, value)

    def set_anim(self, value: "anim_t") -> None:
        return _lvgl.style_set_anim(self, value)

    def set_anim_duration(self, value: _lvgl.uint32_t) -> None:
        return _lvgl.style_set_anim_duration(self, value)

    def set_transition(self, value: "style_transition_dsc_t") -> None:
        return _lvgl.style_set_transition(self, value)

    def set_blend_mode(self, value: _lvgl.blend_mode_t) -> None:
        return _lvgl.style_set_blend_mode(self, value)

    def set_layout(self, value: _lvgl.uint16_t) -> None:
        return _lvgl.style_set_layout(self, value)

    def set_base_dir(self, value: _lvgl.base_dir_t) -> None:
        return _lvgl.style_set_base_dir(self, value)

    def set_bitmap_mask_src(self, value: _lvgl.void) -> None:
        return _lvgl.style_set_bitmap_mask_src(self, value)

    def set_rotary_sensitivity(self, value: _lvgl.uint32_t) -> None:
        return _lvgl.style_set_rotary_sensitivity(self, value)

    def set_flex_flow(self, value: _lvgl.flex_flow_t) -> None:
        return _lvgl.style_set_flex_flow(self, value)

    def set_flex_main_place(self, value: _lvgl.flex_align_t) -> None:
        return _lvgl.style_set_flex_main_place(self, value)

    def set_flex_cross_place(self, value: _lvgl.flex_align_t) -> None:
        return _lvgl.style_set_flex_cross_place(self, value)

    def set_flex_track_place(self, value: _lvgl.flex_align_t) -> None:
        return _lvgl.style_set_flex_track_place(self, value)

    def set_flex_grow(self, value: _lvgl.uint8_t) -> None:
        return _lvgl.style_set_flex_grow(self, value)

    def set_grid_column_dsc_array(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_grid_column_dsc_array(self, value)

    def set_grid_column_align(self, value: _lvgl.grid_align_t) -> None:
        return _lvgl.style_set_grid_column_align(self, value)

    def set_grid_row_dsc_array(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_grid_row_dsc_array(self, value)

    def set_grid_row_align(self, value: _lvgl.grid_align_t) -> None:
        return _lvgl.style_set_grid_row_align(self, value)

    def set_grid_cell_column_pos(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_grid_cell_column_pos(self, value)

    def set_grid_cell_x_align(self, value: _lvgl.grid_align_t) -> None:
        return _lvgl.style_set_grid_cell_x_align(self, value)

    def set_grid_cell_column_span(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_grid_cell_column_span(self, value)

    def set_grid_cell_row_pos(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_grid_cell_row_pos(self, value)

    def set_grid_cell_y_align(self, value: _lvgl.grid_align_t) -> None:
        return _lvgl.style_set_grid_cell_y_align(self, value)

    def set_grid_cell_row_span(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_grid_cell_row_span(self, value)

    def set_size(self, width: _lvgl.int32_t, height: _lvgl.int32_t) -> None:
        return _lvgl.style_set_size(self, width, height)

    def set_pad_all(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_all(self, value)

    def set_pad_hor(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_hor(self, value)

    def set_pad_ver(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_ver(self, value)

    def set_pad_gap(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_pad_gap(self, value)

    def set_margin_hor(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_hor(self, value)

    def set_margin_ver(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_ver(self, value)

    def set_margin_all(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_margin_all(self, value)

    def set_transform_scale(self, value: _lvgl.int32_t) -> None:
        return _lvgl.style_set_transform_scale(self, value)


class style_transition_dsc_t(_lvgl.style_transition_dsc_t):

    def init(self, props: "List", path_cb: "anim_path_cb_t", time: _lvgl.uint32_t, delay: _lvgl.uint32_t, user_data: "Any") -> None:
        return _lvgl.style_transition_dsc_init(self, props, path_cb, time, delay, user_data)


class event_list_t(_lvgl.event_list_t):

    def send(self, e: "event_t", preprocess: _lvgl._Bool) -> _lvgl.result_t:
        return _lvgl.event_send(self, e, preprocess)

    def add(self, cb: "event_cb_t", filter: _lvgl.event_code_t, user_data: "Any") -> "event_dsc_t":
        return _lvgl.event_add(self, cb, filter, user_data)

    def remove_dsc(self, dsc: "event_dsc_t") -> _lvgl._Bool:
        return _lvgl.event_remove_dsc(self, dsc)

    def get_count(self) -> _lvgl.uint32_t:
        return _lvgl.event_get_count(self)

    def get_dsc(self, index: _lvgl.uint32_t) -> "event_dsc_t":
        return _lvgl.event_get_dsc(self, index)

    def remove(self, index: _lvgl.uint32_t) -> _lvgl._Bool:
        return _lvgl.event_remove(self, index)

    def remove_all(self) -> None:
        return _lvgl.event_remove_all(self)


class event_dsc_t(_lvgl.event_dsc_t):

    def get_cb(self) -> "event_cb_t":
        return _lvgl.event_dsc_get_cb(self)

    def get_user_data(self) -> "Any":
        return _lvgl.event_dsc_get_user_data(self)


class event_t(_lvgl.event_t):

    def get_target(self) -> "Any":
        return _lvgl.event_get_target(self)

    def get_current_target(self) -> "Any":
        return _lvgl.event_get_current_target(self)

    def get_code(self) -> _lvgl.event_code_t:
        return _lvgl.event_get_code(self)

    def get_param(self) -> "Any":
        return _lvgl.event_get_param(self)

    def get_user_data(self) -> "Any":
        return _lvgl.event_get_user_data(self)

    def stop_bubbling(self) -> None:
        return _lvgl.event_stop_bubbling(self)

    def stop_trickling(self) -> None:
        return _lvgl.event_stop_trickling(self)

    def stop_processing(self) -> None:
        return _lvgl.event_stop_processing(self)

    def free_user_data_cb(self) -> None:
        return _lvgl.event_free_user_data_cb(self)

    def get_invalidated_area(self) -> "area_t":
        return _lvgl.event_get_invalidated_area(self)

    def get_current_target_obj(self) -> "obj":
        return _wrap_obj(_lvgl.event_get_current_target_obj(self))

    def get_target_obj(self) -> "obj":
        return _wrap_obj(_lvgl.event_get_target_obj(self))

    def get_indev(self) -> "indev_t":
        return _lvgl.event_get_indev(self)

    def get_layer(self) -> "layer_t":
        return _lvgl.event_get_layer(self)

    def get_old_size(self) -> "area_t":
        return _lvgl.event_get_old_size(self)

    def get_key(self) -> _lvgl.uint32_t:
        return _lvgl.event_get_key(self)

    def get_rotary_diff(self) -> _lvgl.int32_t:
        return _lvgl.event_get_rotary_diff(self)

    def get_scroll_anim(self) -> "anim_t":
        return _lvgl.event_get_scroll_anim(self)

    def set_ext_draw_size(self, size: _lvgl.int32_t) -> None:
        return _lvgl.event_set_ext_draw_size(self, size)

    def get_self_size_info(self) -> _lvgl.point_t:
        return _lvgl.event_get_self_size_info(self)

    def get_hit_test_info(self) -> "hit_test_info_t":
        return _lvgl.event_get_hit_test_info(self)

    def get_cover_area(self) -> "area_t":
        return _lvgl.event_get_cover_area(self)

    def set_cover_res(self, res: _lvgl.cover_res_t) -> None:
        return _lvgl.event_set_cover_res(self, res)

    def get_draw_task(self) -> "draw_task_t":
        return _lvgl.event_get_draw_task(self)

    def get_prev_state(self) -> _lvgl.state_t:
        return _lvgl.event_get_prev_state(self)


class display_t(_lvgl.display_t):

    def delete(self) -> None:
        return _lvgl.display_delete(self)

    def set_default(self) -> None:
        return _lvgl.display_set_default(self)

    def get_next(self) -> "display_t":
        return _lvgl.display_get_next(self)

    def set_resolution(self, hor_res: _lvgl.int32_t, ver_res: _lvgl.int32_t) -> None:
        return _lvgl.display_set_resolution(self, hor_res, ver_res)

    def set_physical_resolution(self, hor_res: _lvgl.int32_t, ver_res: _lvgl.int32_t) -> None:
        return _lvgl.display_set_physical_resolution(self, hor_res, ver_res)

    def set_offset(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> None:
        return _lvgl.display_set_offset(self, x, y)

    def set_rotation(self, rotation: _lvgl.display_rotation_t) -> None:
        return _lvgl.display_set_rotation(self, rotation)

    def set_matrix_rotation(self, enable: _lvgl._Bool) -> None:
        return _lvgl.display_set_matrix_rotation(self, enable)

    def set_dpi(self, dpi: _lvgl.int32_t) -> None:
        return _lvgl.display_set_dpi(self, dpi)

    def get_horizontal_resolution(self) -> _lvgl.int32_t:
        return _lvgl.display_get_horizontal_resolution(self)

    def get_vertical_resolution(self) -> _lvgl.int32_t:
        return _lvgl.display_get_vertical_resolution(self)

    def get_original_horizontal_resolution(self) -> _lvgl.int32_t:
        return _lvgl.display_get_original_horizontal_resolution(self)

    def get_original_vertical_resolution(self) -> _lvgl.int32_t:
        return _lvgl.display_get_original_vertical_resolution(self)

    def get_physical_horizontal_resolution(self) -> _lvgl.int32_t:
        return _lvgl.display_get_physical_horizontal_resolution(self)

    def get_physical_vertical_resolution(self) -> _lvgl.int32_t:
        return _lvgl.display_get_physical_vertical_resolution(self)

    def get_offset_x(self) -> _lvgl.int32_t:
        return _lvgl.display_get_offset_x(self)

    def get_offset_y(self) -> _lvgl.int32_t:
        return _lvgl.display_get_offset_y(self)

    def get_rotation(self) -> _lvgl.display_rotation_t:
        return _lvgl.display_get_rotation(self)

    def get_matrix_rotation(self) -> _lvgl._Bool:
        return _lvgl.display_get_matrix_rotation(self)

    def get_dpi(self) -> _lvgl.int32_t:
        return _lvgl.display_get_dpi(self)

    def set_buffers(self, buf1: _lvgl.void, buf2: _lvgl.void, buf_size: _lvgl.uint32_t, render_mode: _lvgl.display_render_mode_t) -> None:
        return _lvgl.display_set_buffers(self, buf1, buf2, buf_size, render_mode)

    def set_buffers_with_stride(self, buf1: _lvgl.void, buf2: _lvgl.void, buf_size: _lvgl.uint32_t, stride: _lvgl.uint32_t, render_mode: _lvgl.display_render_mode_t) -> None:
        return _lvgl.display_set_buffers_with_stride(self, buf1, buf2, buf_size, stride, render_mode)

    def set_draw_buffers(self, buf1: "draw_buf_t", buf2: "draw_buf_t") -> None:
        return _lvgl.display_set_draw_buffers(self, buf1, buf2)

    def set_3rd_draw_buffer(self, buf3: "draw_buf_t") -> None:
        return _lvgl.display_set_3rd_draw_buffer(self, buf3)

    def set_render_mode(self, render_mode: _lvgl.display_render_mode_t) -> None:
        return _lvgl.display_set_render_mode(self, render_mode)

    def set_flush_cb(self, flush_cb: "display_flush_cb_t") -> None:
        return _lvgl.display_set_flush_cb(self, flush_cb)

    def set_flush_wait_cb(self, wait_cb: "display_flush_wait_cb_t") -> None:
        return _lvgl.display_set_flush_wait_cb(self, wait_cb)

    def set_color_format(self, color_format: _lvgl.color_format_t) -> None:
        return _lvgl.display_set_color_format(self, color_format)

    def get_color_format(self) -> _lvgl.color_format_t:
        return _lvgl.display_get_color_format(self)

    def set_tile_cnt(self, tile_cnt: _lvgl.uint32_t) -> None:
        return _lvgl.display_set_tile_cnt(self, tile_cnt)

    def get_tile_cnt(self) -> _lvgl.uint32_t:
        return _lvgl.display_get_tile_cnt(self)

    def set_antialiasing(self, en: _lvgl._Bool) -> None:
        return _lvgl.display_set_antialiasing(self, en)

    def get_antialiasing(self) -> _lvgl._Bool:
        return _lvgl.display_get_antialiasing(self)

    def flush_ready(self) -> None:
        return _lvgl.display_flush_ready(self)

    def flush_is_last(self) -> _lvgl._Bool:
        return _lvgl.display_flush_is_last(self)

    def is_double_buffered(self) -> _lvgl._Bool:
        return _lvgl.display_is_double_buffered(self)

    def get_render_mode(self) -> _lvgl.display_render_mode_t:
        return _lvgl.display_get_render_mode(self)

    def get_screen_active(self) -> "obj":
        return _wrap_obj(_lvgl.display_get_screen_active(self))

    def get_screen_prev(self) -> "obj":
        return _wrap_obj(_lvgl.display_get_screen_prev(self))

    def get_screen_loading(self) -> "obj":
        return _wrap_obj(_lvgl.display_get_screen_loading(self))

    def get_layer_top(self) -> "obj":
        return _wrap_obj(_lvgl.display_get_layer_top(self))

    def get_layer_sys(self) -> "obj":
        return _wrap_obj(_lvgl.display_get_layer_sys(self))

    def get_layer_bottom(self) -> "obj":
        return _wrap_obj(_lvgl.display_get_layer_bottom(self))

    def add_event_cb(self, event_cb: "event_cb_t", filter: _lvgl.event_code_t, user_data: "Any") -> None:
        return _lvgl.display_add_event_cb(self, event_cb, filter, user_data)

    def get_event_count(self) -> _lvgl.uint32_t:
        return _lvgl.display_get_event_count(self)

    def get_event_dsc(self, index: _lvgl.uint32_t) -> "event_dsc_t":
        return _lvgl.display_get_event_dsc(self, index)

    def delete_event(self, index: _lvgl.uint32_t) -> _lvgl._Bool:
        return _lvgl.display_delete_event(self, index)

    def remove_event_cb_with_user_data(self, event_cb: "event_cb_t", user_data: "Any") -> _lvgl.uint32_t:
        return _lvgl.display_remove_event_cb_with_user_data(self, event_cb, user_data)

    def send_event(self, code: _lvgl.event_code_t, param: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.display_send_event(self, code, param)

    def set_theme(self, th: "theme_t") -> None:
        return _lvgl.display_set_theme(self, th)

    def get_theme(self) -> "theme_t":
        return _lvgl.display_get_theme(self)

    def get_inactive_time(self) -> _lvgl.uint32_t:
        return _lvgl.display_get_inactive_time(self)

    def trigger_activity(self) -> None:
        return _lvgl.display_trigger_activity(self)

    def enable_invalidation(self, en: _lvgl._Bool) -> None:
        return _lvgl.display_enable_invalidation(self, en)

    def is_invalidation_enabled(self) -> _lvgl._Bool:
        return _lvgl.display_is_invalidation_enabled(self)

    def get_refr_timer(self) -> "timer_t":
        return _lvgl.display_get_refr_timer(self)

    def delete_refr_timer(self) -> None:
        return _lvgl.display_delete_refr_timer(self)

    def register_vsync_event(self, event_cb: "event_cb_t", user_data: "Any") -> _lvgl._Bool:
        return _lvgl.display_register_vsync_event(self, event_cb, user_data)

    def unregister_vsync_event(self, event_cb: "event_cb_t", user_data: "Any") -> _lvgl._Bool:
        return _lvgl.display_unregister_vsync_event(self, event_cb, user_data)

    def send_vsync_event(self, param: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.display_send_vsync_event(self, param)

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.display_set_user_data(self, user_data)

    def set_driver_data(self, driver_data: _lvgl.void) -> None:
        return _lvgl.display_set_driver_data(self, driver_data)

    def get_user_data(self) -> "Any":
        return _lvgl.display_get_user_data(self)

    def get_driver_data(self) -> "Any":
        return _lvgl.display_get_driver_data(self)

    def get_buf_active(self) -> "draw_buf_t":
        return _lvgl.display_get_buf_active(self)

    def rotate_area(self, area: "area_t") -> None:
        return _lvgl.display_rotate_area(self, area)

    def rotate_point(self, point: _lvgl.point_t) -> None:
        return _lvgl.display_rotate_point(self, point)

    def get_draw_buf_size(self) -> _lvgl.uint32_t:
        return _lvgl.display_get_draw_buf_size(self)

    def get_invalidated_draw_buf_size(self, width: _lvgl.uint32_t, height: _lvgl.uint32_t) -> _lvgl.uint32_t:
        return _lvgl.display_get_invalidated_draw_buf_size(self, width, height)

    def dpx(self, n: _lvgl.int32_t) -> _lvgl.int32_t:
        return _lvgl.display_dpx(self, n)


class fs_drv_t(_lvgl.fs_drv_t):

    def init(self) -> None:
        return _lvgl.fs_drv_init(self)

    def register(self) -> None:
        return _lvgl.fs_drv_register(self)


class fs_file_t(_lvgl.fs_file_t):

    def open(self, path: _lvgl.char, mode: _lvgl.fs_mode_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_open(self, path, mode)

    def close(self) -> _lvgl.fs_res_t:
        return _lvgl.fs_close(self)

    def read(self, buf: _lvgl.void, btr: _lvgl.uint32_t, br: _lvgl.uint32_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_read(self, buf, btr, br)

    def write(self, buf: _lvgl.void, btw: _lvgl.uint32_t, bw: _lvgl.uint32_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_write(self, buf, btw, bw)

    def seek(self, pos: _lvgl.uint32_t, whence: _lvgl.fs_whence_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_seek(self, pos, whence)

    def tell(self, pos: _lvgl.uint32_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_tell(self, pos)

    def get_size(self, size_res: _lvgl.uint32_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_get_size(self, size_res)


class fs_path_ex_t(_lvgl.fs_path_ex_t):

    def make_path_from_buffer(self, letter: _lvgl.char, buf: _lvgl.void, size: _lvgl.uint32_t, ext: _lvgl.char) -> None:
        return _lvgl.fs_make_path_from_buffer(self, letter, buf, size, ext)

    def get_buffer_from_path(self, buffer: _lvgl.void, size: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.fs_get_buffer_from_path(self, buffer, size)


class fs_dir_t(_lvgl.fs_dir_t):

    def open(self, path: _lvgl.char) -> _lvgl.fs_res_t:
        return _lvgl.fs_dir_open(self, path)

    def read(self, fn: _lvgl.char, fn_len: _lvgl.uint32_t) -> _lvgl.fs_res_t:
        return _lvgl.fs_dir_read(self, fn, fn_len)

    def close(self) -> _lvgl.fs_res_t:
        return _lvgl.fs_dir_close(self)


class image_decoder_dsc_t(_lvgl.image_decoder_dsc_t):

    def open(self, src: _lvgl.void, args: "image_decoder_args_t") -> _lvgl.result_t:
        return _lvgl.image_decoder_open(self, src, args)

    def get_area(self, full_area: "area_t", decoded_area: "area_t") -> _lvgl.result_t:
        return _lvgl.image_decoder_get_area(self, full_area, decoded_area)

    def close(self) -> None:
        return _lvgl.image_decoder_close(self)

    def post_process(self, decoded: "draw_buf_t") -> "draw_buf_t":
        return _lvgl.image_decoder_post_process(self, decoded)


class image_decoder_t(_lvgl.image_decoder_t):

    def delete(self) -> None:
        return _lvgl.image_decoder_delete(self)

    def get_next(self) -> "image_decoder_t":
        return _lvgl.image_decoder_get_next(self)

    def set_info_cb(self, info_cb: "image_decoder_info_f_t") -> None:
        return _lvgl.image_decoder_set_info_cb(self, info_cb)

    def set_open_cb(self, open_cb: "image_decoder_open_f_t") -> None:
        return _lvgl.image_decoder_set_open_cb(self, open_cb)

    def set_get_area_cb(self, read_line_cb: "image_decoder_get_area_cb_t") -> None:
        return _lvgl.image_decoder_set_get_area_cb(self, read_line_cb)

    def set_close_cb(self, close_cb: "image_decoder_close_f_t") -> None:
        return _lvgl.image_decoder_set_close_cb(self, close_cb)

    def add_to_cache(self, search_key: "image_cache_data_t", decoded: "draw_buf_t", user_data: "Any") -> "cache_entry_t":
        return _lvgl.image_decoder_add_to_cache(self, search_key, decoded, user_data)


class layer_t(_lvgl.layer_t):

    def init(self) -> None:
        return _lvgl.layer_init(self)

    def reset(self) -> None:
        return _lvgl.layer_reset(self)


class draw_rect_dsc_t(_lvgl.draw_rect_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_rect_dsc_init(self)


class draw_fill_dsc_t(_lvgl.draw_fill_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_fill_dsc_init(self)


class draw_border_dsc_t(_lvgl.draw_border_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_border_dsc_init(self)


class draw_box_shadow_dsc_t(_lvgl.draw_box_shadow_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_box_shadow_dsc_init(self)


class draw_letter_dsc_t(_lvgl.draw_letter_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_letter_dsc_init(self)


class draw_label_dsc_t(_lvgl.draw_label_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_label_dsc_init(self)


class draw_glyph_dsc_t(_lvgl.draw_glyph_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_glyph_dsc_init(self)


class draw_image_dsc_t(_lvgl.draw_image_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_image_dsc_init(self)


class draw_line_dsc_t(_lvgl.draw_line_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_line_dsc_init(self)


class draw_arc_dsc_t(_lvgl.draw_arc_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_arc_dsc_init(self)


class draw_triangle_dsc_t(_lvgl.draw_triangle_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_triangle_dsc_init(self)


class draw_blur_dsc_t(_lvgl.draw_blur_dsc_t):

    def init(self) -> None:
        return _lvgl.draw_blur_dsc_init(self)


class obj_class_t(_lvgl.obj_class_t):

    def create_obj(self, parent: "obj") -> "obj":
        return _wrap_obj(_lvgl.obj_class_create_obj(self, parent))

    def event_base(self, e: "event_t") -> _lvgl.result_t:
        return _lvgl.obj_event_base(self, e)


class group_t(_lvgl.group_t):

    def delete(self) -> None:
        return _lvgl.group_delete(self)

    def set_default(self) -> None:
        return _lvgl.group_set_default(self)

    def add_obj(self, obj: "obj") -> None:
        return _lvgl.group_add_obj(self, obj)

    def remove_all_objs(self) -> None:
        return _lvgl.group_remove_all_objs(self)

    def focus_next(self) -> None:
        return _lvgl.group_focus_next(self)

    def focus_prev(self) -> None:
        return _lvgl.group_focus_prev(self)

    def focus_freeze(self, en: _lvgl._Bool) -> None:
        return _lvgl.group_focus_freeze(self, en)

    def send_data(self, c: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.group_send_data(self, c)

    def set_focus_cb(self, focus_cb: "group_focus_cb_t") -> None:
        return _lvgl.group_set_focus_cb(self, focus_cb)

    def set_edge_cb(self, edge_cb: "group_edge_cb_t") -> None:
        return _lvgl.group_set_edge_cb(self, edge_cb)

    def set_refocus_policy(self, policy: _lvgl.group_refocus_policy_t) -> None:
        return _lvgl.group_set_refocus_policy(self, policy)

    def set_editing(self, edit: _lvgl._Bool) -> None:
        return _lvgl.group_set_editing(self, edit)

    def set_wrap(self, en: _lvgl._Bool) -> None:
        return _lvgl.group_set_wrap(self, en)

    def get_focused(self) -> "obj":
        return _wrap_obj(_lvgl.group_get_focused(self))

    def get_focus_cb(self) -> "group_focus_cb_t":
        return _lvgl.group_get_focus_cb(self)

    def get_edge_cb(self) -> "group_edge_cb_t":
        return _lvgl.group_get_edge_cb(self)

    def get_editing(self) -> _lvgl._Bool:
        return _lvgl.group_get_editing(self)

    def get_wrap(self) -> _lvgl._Bool:
        return _lvgl.group_get_wrap(self)

    def get_obj_count(self) -> _lvgl.uint32_t:
        return _lvgl.group_get_obj_count(self)

    def get_obj_by_index(self, index: _lvgl.uint32_t) -> "obj":
        return _wrap_obj(_lvgl.group_get_obj_by_index(self, index))

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.group_set_user_data(self, user_data)

    def get_user_data(self) -> "Any":
        return _lvgl.group_get_user_data(self)


class indev_t(_lvgl.indev_t):

    def delete(self) -> None:
        return _lvgl.indev_delete(self)

    def get_next(self) -> "indev_t":
        return _lvgl.indev_get_next(self)

    def read(self) -> None:
        return _lvgl.indev_read(self)

    def enable(self, enable: _lvgl._Bool) -> None:
        return _lvgl.indev_enable(self, enable)

    def set_type(self, indev_type: _lvgl.indev_type_t) -> None:
        return _lvgl.indev_set_type(self, indev_type)

    def set_read_cb(self, read_cb: "indev_read_cb_t") -> None:
        return _lvgl.indev_set_read_cb(self, read_cb)

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.indev_set_user_data(self, user_data)

    def set_driver_data(self, driver_data: _lvgl.void) -> None:
        return _lvgl.indev_set_driver_data(self, driver_data)

    def set_display(self, disp: "display_t") -> None:
        return _lvgl.indev_set_display(self, disp)

    def set_long_press_time(self, long_press_time: _lvgl.uint16_t) -> None:
        return _lvgl.indev_set_long_press_time(self, long_press_time)

    def set_long_press_repeat_time(self, long_press_repeat_time: _lvgl.uint16_t) -> None:
        return _lvgl.indev_set_long_press_repeat_time(self, long_press_repeat_time)

    def set_scroll_limit(self, scroll_limit: _lvgl.uint8_t) -> None:
        return _lvgl.indev_set_scroll_limit(self, scroll_limit)

    def set_scroll_throw(self, scroll_throw: _lvgl.uint8_t) -> None:
        return _lvgl.indev_set_scroll_throw(self, scroll_throw)

    def set_gesture_min_velocity(self, min_velocity: _lvgl.uint8_t) -> None:
        return _lvgl.indev_set_gesture_min_velocity(self, min_velocity)

    def set_gesture_min_distance(self, min_distance: _lvgl.uint8_t) -> None:
        return _lvgl.indev_set_gesture_min_distance(self, min_distance)

    def get_type(self) -> _lvgl.indev_type_t:
        return _lvgl.indev_get_type(self)

    def get_read_cb(self) -> "indev_read_cb_t":
        return _lvgl.indev_get_read_cb(self)

    def get_state(self) -> _lvgl.indev_state_t:
        return _lvgl.indev_get_state(self)

    def get_group(self) -> "group_t":
        return _lvgl.indev_get_group(self)

    def get_display(self) -> "display_t":
        return _lvgl.indev_get_display(self)

    def get_user_data(self) -> "Any":
        return _lvgl.indev_get_user_data(self)

    def get_driver_data(self) -> "Any":
        return _lvgl.indev_get_driver_data(self)

    def get_press_moved(self) -> _lvgl._Bool:
        return _lvgl.indev_get_press_moved(self)

    def reset(self, obj: "obj") -> None:
        return _lvgl.indev_reset(self, obj)

    def stop_processing(self) -> None:
        return _lvgl.indev_stop_processing(self)

    def reset_long_press(self) -> None:
        return _lvgl.indev_reset_long_press(self)

    def set_cursor(self, cur_obj: "obj") -> None:
        return _lvgl.indev_set_cursor(self, cur_obj)

    def set_group(self, group: "group_t") -> None:
        return _lvgl.indev_set_group(self, group)

    def set_button_points(self, points: "List") -> None:
        return _lvgl.indev_set_button_points(self, points)

    def get_point(self, point: _lvgl.point_t) -> None:
        return _lvgl.indev_get_point(self, point)

    def get_gesture_dir(self) -> _lvgl.dir_t:
        return _lvgl.indev_get_gesture_dir(self)

    def get_key(self) -> _lvgl.uint32_t:
        return _lvgl.indev_get_key(self)

    def get_short_click_streak(self) -> _lvgl.uint8_t:
        return _lvgl.indev_get_short_click_streak(self)

    def get_scroll_dir(self) -> _lvgl.dir_t:
        return _lvgl.indev_get_scroll_dir(self)

    def get_scroll_obj(self) -> "obj":
        return _wrap_obj(_lvgl.indev_get_scroll_obj(self))

    def get_vect(self, point: _lvgl.point_t) -> None:
        return _lvgl.indev_get_vect(self, point)

    def get_cursor(self) -> "obj":
        return _wrap_obj(_lvgl.indev_get_cursor(self))

    def wait_release(self) -> None:
        return _lvgl.indev_wait_release(self)

    def get_read_timer(self) -> "timer_t":
        return _lvgl.indev_get_read_timer(self)

    def set_mode(self, mode: _lvgl.indev_mode_t) -> None:
        return _lvgl.indev_set_mode(self, mode)

    def get_mode(self) -> _lvgl.indev_mode_t:
        return _lvgl.indev_get_mode(self)

    def add_event_cb(self, event_cb: "event_cb_t", filter: _lvgl.event_code_t, user_data: "Any") -> None:
        return _lvgl.indev_add_event_cb(self, event_cb, filter, user_data)

    def get_event_count(self) -> _lvgl.uint32_t:
        return _lvgl.indev_get_event_count(self)

    def get_event_dsc(self, index: _lvgl.uint32_t) -> "event_dsc_t":
        return _lvgl.indev_get_event_dsc(self, index)

    def remove_event(self, index: _lvgl.uint32_t) -> _lvgl._Bool:
        return _lvgl.indev_remove_event(self, index)

    def remove_event_cb_with_user_data(self, event_cb: "event_cb_t", user_data: "Any") -> _lvgl.uint32_t:
        return _lvgl.indev_remove_event_cb_with_user_data(self, event_cb, user_data)

    def send_event(self, code: _lvgl.event_code_t, param: _lvgl.void) -> _lvgl.result_t:
        return _lvgl.indev_send_event(self, code, param)

    def set_key_remap_cb(self, remap_cb: "indev_key_remap_cb_t") -> None:
        return _lvgl.indev_set_key_remap_cb(self, remap_cb)


class subject_t(_lvgl.subject_t):

    def init_int(self, value: _lvgl.int32_t) -> None:
        return _lvgl.subject_init_int(self, value)

    def set_int(self, value: _lvgl.int32_t) -> None:
        return _lvgl.subject_set_int(self, value)

    def get_int(self) -> _lvgl.int32_t:
        return _lvgl.subject_get_int(self)

    def get_previous_int(self) -> _lvgl.int32_t:
        return _lvgl.subject_get_previous_int(self)

    def set_min_value_int(self, min_value: _lvgl.int32_t) -> None:
        return _lvgl.subject_set_min_value_int(self, min_value)

    def set_max_value_int(self, max_value: _lvgl.int32_t) -> None:
        return _lvgl.subject_set_max_value_int(self, max_value)

    def init_string(self, buf: _lvgl.char, prev_buf: _lvgl.char, size: _lvgl.size_t, value: _lvgl.char) -> None:
        return _lvgl.subject_init_string(self, buf, prev_buf, size, value)

    def copy_string(self, buf: _lvgl.char) -> None:
        return _lvgl.subject_copy_string(self, buf)

    def snprintf(self, format: _lvgl.char, *args) -> None:
        return _lvgl.subject_snprintf(self, format, *args)

    def get_string(self) -> _lvgl.char:
        return _lvgl.subject_get_string(self)

    def get_previous_string(self) -> _lvgl.char:
        return _lvgl.subject_get_previous_string(self)

    def init_pointer(self, value: _lvgl.void) -> None:
        return _lvgl.subject_init_pointer(self, value)

    def set_pointer(self, ptr: _lvgl.void) -> None:
        return _lvgl.subject_set_pointer(self, ptr)

    def get_pointer(self) -> "Any":
        return _lvgl.subject_get_pointer(self)

    def get_previous_pointer(self) -> "Any":
        return _lvgl.subject_get_previous_pointer(self)

    def init_color(self, color: "color_t") -> None:
        return _lvgl.subject_init_color(self, color)

    def set_color(self, color: "color_t") -> None:
        return _lvgl.subject_set_color(self, color)

    def get_color(self) -> "color_t":
        return _lvgl.subject_get_color(self)

    def get_previous_color(self) -> "color_t":
        return _lvgl.subject_get_previous_color(self)

    def init_group(self, list: "List", list_len: _lvgl.uint32_t) -> None:
        return _lvgl.subject_init_group(self, list, list_len)

    def deinit(self) -> None:
        return _lvgl.subject_deinit(self)

    def get_group_element(self, index: _lvgl.int32_t) -> "subject_t":
        return _lvgl.subject_get_group_element(self, index)

    def add_observer(self, observer_cb: "observer_cb_t", user_data: "Any") -> "observer_t":
        return _lvgl.subject_add_observer(self, observer_cb, user_data)

    def add_observer_obj(self, observer_cb: "observer_cb_t", obj: "obj", user_data: "Any") -> "observer_t":
        return _lvgl.subject_add_observer_obj(self, observer_cb, obj, user_data)

    def add_observer_with_target(self, observer_cb: "observer_cb_t", target: _lvgl.void, user_data: "Any") -> "observer_t":
        return _lvgl.subject_add_observer_with_target(self, observer_cb, target, user_data)

    def notify(self) -> None:
        return _lvgl.subject_notify(self)


class observer_t(_lvgl.observer_t):

    def remove(self) -> None:
        return _lvgl.observer_remove(self)

    def get_target(self) -> "Any":
        return _lvgl.observer_get_target(self)

    def get_target_obj(self) -> "obj":
        return _wrap_obj(_lvgl.observer_get_target_obj(self))

    def get_user_data(self) -> "Any":
        return _lvgl.observer_get_user_data(self)


class scale_section_t(_lvgl.scale_section_t):

    def set_range(self, min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.scale_section_set_range(self, min, max)

    def set_style(self, part: _lvgl.part_t, section_part_style: "style_t") -> None:
        return _lvgl.scale_section_set_style(self, part, section_part_style)


class span_t(_lvgl.span_t):

    def set_text(self, text: _lvgl.char) -> None:
        return _lvgl.span_set_text(self, text)

    def set_text_fmt(self, fmt: _lvgl.char, *args) -> None:
        return _lvgl.span_set_text_fmt(self, fmt, *args)

    def set_text_static(self, text: _lvgl.char) -> None:
        return _lvgl.span_set_text_static(self, text)

    def get_style(self) -> "style_t":
        return _lvgl.span_get_style(self)

    def get_text(self) -> _lvgl.char:
        return _lvgl.span_get_text(self)


class theme_t(_lvgl.theme_t):

    def copy(self, src: "theme_t") -> None:
        return _lvgl.theme_copy(self, src)

    def set_parent(self, parent: "theme_t") -> None:
        return _lvgl.theme_set_parent(self, parent)

    def set_apply_cb(self, apply_cb: "theme_apply_cb_t") -> None:
        return _lvgl.theme_set_apply_cb(self, apply_cb)

    def delete(self) -> None:
        return _lvgl.theme_delete(self)


class demo_args_t(_lvgl.demo_args_t):

    def init(self) -> None:
        return _lvgl.demo_args_init(self)


class tree_class_t(_lvgl.tree_class_t):

    def node_create(self, parent: "tree_node_t") -> "tree_node_t":
        return _lvgl.tree_node_create(self, parent)


class layout_callbacks_t(_lvgl.layout_callbacks_t):

    def create(self, user_data: "Any") -> _lvgl.uint32_t:
        return _lvgl.layout_create(self, user_data)


class draw_layer(_lvgl.layer_t):
    
    class BUF:
        ALIGN = _lvgl.DRAW_BUF_ALIGN
        STRIDE_ALIGN = _lvgl.DRAW_BUF_STRIDE_ALIGN
    
    class TASK_STATE:
        BLOCKED = _lvgl.DRAW_TASK_STATE_BLOCKED
        FINISHED = _lvgl.DRAW_TASK_STATE_FINISHED
        IN_PROGRESS = _lvgl.DRAW_TASK_STATE_IN_PROGRESS
        QUEUED = _lvgl.DRAW_TASK_STATE_QUEUED
        WAITING = _lvgl.DRAW_TASK_STATE_WAITING
        TYPE_ARC = _lvgl.DRAW_TASK_TYPE_ARC
        TYPE_BLUR = _lvgl.DRAW_TASK_TYPE_BLUR
        TYPE_BORDER = _lvgl.DRAW_TASK_TYPE_BORDER
        TYPE_BOX_SHADOW = _lvgl.DRAW_TASK_TYPE_BOX_SHADOW
        TYPE_FILL = _lvgl.DRAW_TASK_TYPE_FILL
        TYPE_IMAGE = _lvgl.DRAW_TASK_TYPE_IMAGE
        TYPE_LABEL = _lvgl.DRAW_TASK_TYPE_LABEL
        TYPE_LAYER = _lvgl.DRAW_TASK_TYPE_LAYER
        TYPE_LETTER = _lvgl.DRAW_TASK_TYPE_LETTER
        TYPE_LINE = _lvgl.DRAW_TASK_TYPE_LINE
        TYPE_MASK_BITMAP = _lvgl.DRAW_TASK_TYPE_MASK_BITMAP
        TYPE_MASK_RECTANGLE = _lvgl.DRAW_TASK_TYPE_MASK_RECTANGLE
        TYPE_NONE = _lvgl.DRAW_TASK_TYPE_NONE
        TYPE_TRIANGLE = _lvgl.DRAW_TASK_TYPE_TRIANGLE

    def __init__(self, parent_layer: _lvgl.layer_t, color_format: _lvgl.color_format_t, area: _lvgl.area_t):
        for arg in (parent_layer, color_format, area,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.draw_layer_create(parent_layer, color_format, area)
            cls.cast(self)


    def init(self, parent_layer: "layer_t", color_format: _lvgl.color_format_t, area: "area_t") -> None:
        return _lvgl.draw_layer_init(self, parent_layer, color_format, area)

    def alloc_buf(self) -> "Any":
        return _lvgl.draw_layer_alloc_buf(self)

    def go_to_xy(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> "Any":
        return _lvgl.draw_layer_go_to_xy(self, x, y)

    def create_drop_shadow(self, base: "draw_dsc_base_t", area: "area_t") -> "layer_t":
        return _lvgl.draw_layer_create_drop_shadow(self, base, area)

    def finish_drop_shadow(self, base: "draw_dsc_base_t") -> None:
        return _lvgl.draw_layer_finish_drop_shadow(self, base)


class obj(_lvgl.obj_t):
    
    class CLASS_THEME_INHERITABLE:
        FALSE = _lvgl.OBJ_CLASS_THEME_INHERITABLE_FALSE
        TRUE = _lvgl.OBJ_CLASS_THEME_INHERITABLE_TRUE
    
    class CLASS_GROUP_DEF:
        FALSE = _lvgl.OBJ_CLASS_GROUP_DEF_FALSE
        INHERIT = _lvgl.OBJ_CLASS_GROUP_DEF_INHERIT
        TRUE = _lvgl.OBJ_CLASS_GROUP_DEF_TRUE
    
    class CLASS_EDITABLE:
        FALSE = _lvgl.OBJ_CLASS_EDITABLE_FALSE
        INHERIT = _lvgl.OBJ_CLASS_EDITABLE_INHERIT
        TRUE = _lvgl.OBJ_CLASS_EDITABLE_TRUE
    
    class FLAG:
        ADV_HITTEST = _lvgl.OBJ_FLAG_ADV_HITTEST
        CHECKABLE = _lvgl.OBJ_FLAG_CHECKABLE
        CLICKABLE = _lvgl.OBJ_FLAG_CLICKABLE
        CLICK_FOCUSABLE = _lvgl.OBJ_FLAG_CLICK_FOCUSABLE
        EVENT_BUBBLE = _lvgl.OBJ_FLAG_EVENT_BUBBLE
        EVENT_TRICKLE = _lvgl.OBJ_FLAG_EVENT_TRICKLE
        FLEX_IN_NEW_TRACK = _lvgl.OBJ_FLAG_FLEX_IN_NEW_TRACK
        FLOATING = _lvgl.OBJ_FLAG_FLOATING
        GESTURE_BUBBLE = _lvgl.OBJ_FLAG_GESTURE_BUBBLE
        HIDDEN = _lvgl.OBJ_FLAG_HIDDEN
        IGNORE_LAYOUT = _lvgl.OBJ_FLAG_IGNORE_LAYOUT
        LAYOUT_1 = _lvgl.OBJ_FLAG_LAYOUT_1
        LAYOUT_2 = _lvgl.OBJ_FLAG_LAYOUT_2
        OVERFLOW_VISIBLE = _lvgl.OBJ_FLAG_OVERFLOW_VISIBLE
        PRESS_LOCK = _lvgl.OBJ_FLAG_PRESS_LOCK
        SCROLLABLE = _lvgl.OBJ_FLAG_SCROLLABLE
        SCROLL_CHAIN = _lvgl.OBJ_FLAG_SCROLL_CHAIN
        SCROLL_CHAIN_HOR = _lvgl.OBJ_FLAG_SCROLL_CHAIN_HOR
        SCROLL_CHAIN_VER = _lvgl.OBJ_FLAG_SCROLL_CHAIN_VER
        SCROLL_ELASTIC = _lvgl.OBJ_FLAG_SCROLL_ELASTIC
        SCROLL_MOMENTUM = _lvgl.OBJ_FLAG_SCROLL_MOMENTUM
        SCROLL_ONE = _lvgl.OBJ_FLAG_SCROLL_ONE
        SCROLL_ON_FOCUS = _lvgl.OBJ_FLAG_SCROLL_ON_FOCUS
        SCROLL_WITH_ARROW = _lvgl.OBJ_FLAG_SCROLL_WITH_ARROW
        SEND_DRAW_TASK_EVENTS = _lvgl.OBJ_FLAG_SEND_DRAW_TASK_EVENTS
        SNAPPABLE = _lvgl.OBJ_FLAG_SNAPPABLE
        STATE_TRICKLE = _lvgl.OBJ_FLAG_STATE_TRICKLE
        USER_1 = _lvgl.OBJ_FLAG_USER_1
        USER_2 = _lvgl.OBJ_FLAG_USER_2
        USER_3 = _lvgl.OBJ_FLAG_USER_3
        USER_4 = _lvgl.OBJ_FLAG_USER_4
        WIDGET_1 = _lvgl.OBJ_FLAG_WIDGET_1
        WIDGET_2 = _lvgl.OBJ_FLAG_WIDGET_2
    
    class POINT_TRANSFORM:
        FLAG_INVERSE = _lvgl.OBJ_POINT_TRANSFORM_FLAG_INVERSE
        FLAG_INVERSE_RECURSIVE = _lvgl.OBJ_POINT_TRANSFORM_FLAG_INVERSE_RECURSIVE
        FLAG_NONE = _lvgl.OBJ_POINT_TRANSFORM_FLAG_NONE
        FLAG_RECURSIVE = _lvgl.OBJ_POINT_TRANSFORM_FLAG_RECURSIVE
    
    class TREE_WALK:
        END = _lvgl.OBJ_TREE_WALK_END
        NEXT = _lvgl.OBJ_TREE_WALK_NEXT
        SKIP_CHILDREN = _lvgl.OBJ_TREE_WALK_SKIP_CHILDREN

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.obj_create(parent)
            cls.cast(self)

    def __eq__(self, other):
        if not hasattr(other, '_obj'):
            return NotImplemented
        return self._obj == other._obj

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self):
        ptr = _lvgl._lib_lvgl.ffi.cast('uintptr_t', self._obj)
        return hash(int(ptr))

    def set_flex_flow(self, flow: _lvgl.flex_flow_t) -> None:
        return _lvgl.obj_set_flex_flow(self, flow)

    def set_flex_align(self, main_place: _lvgl.flex_align_t, cross_place: _lvgl.flex_align_t, track_cross_place: _lvgl.flex_align_t) -> None:
        return _lvgl.obj_set_flex_align(self, main_place, cross_place, track_cross_place)

    def set_flex_grow(self, grow: _lvgl.uint8_t) -> None:
        return _lvgl.obj_set_flex_grow(self, grow)

    def set_grid_dsc_array(self, col_dsc: "List", row_dsc: "List") -> None:
        return _lvgl.obj_set_grid_dsc_array(self, col_dsc, row_dsc)

    def set_grid_align(self, column_align: _lvgl.grid_align_t, row_align: _lvgl.grid_align_t) -> None:
        return _lvgl.obj_set_grid_align(self, column_align, row_align)

    def set_grid_cell(self, column_align: _lvgl.grid_align_t, col_pos: _lvgl.int32_t, col_span: _lvgl.int32_t, row_align: _lvgl.grid_align_t, row_pos: _lvgl.int32_t, row_span: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_grid_cell(self, column_align, col_pos, col_span, row_align, row_pos, row_span)

    def delete(self) -> None:
        refs = _collect_obj_release_refs(self)
        result = _lvgl.obj_delete(self)
        _release_collected_obj_refs(refs)
        return result

    def clean(self) -> None:
        return _lvgl.obj_clean(self)

    def delete_delayed(self, delay_ms: _lvgl.uint32_t) -> None:
        return _lvgl.obj_delete_delayed(self, delay_ms)

    def delete_async(self) -> None:
        return _lvgl.obj_delete_async(self)

    def set_parent(self, parent: "obj") -> None:
        return _lvgl.obj_set_parent(self, parent)

    def swap(self, obj2: "obj") -> None:
        return _lvgl.obj_swap(self, obj2)

    def move_to_index(self, index: _lvgl.int32_t) -> None:
        return _lvgl.obj_move_to_index(self, index)

    def get_screen(self) -> "obj":
        return _wrap_obj(_lvgl.obj_get_screen(self))

    def get_display(self) -> "display_t":
        return _lvgl.obj_get_display(self)

    def get_parent(self) -> "obj":
        return _wrap_obj(_lvgl.obj_get_parent(self))

    def get_child(self, idx: _lvgl.int32_t) -> "obj":
        return _wrap_obj(_lvgl.obj_get_child(self, idx))

    def get_child_by_type(self, idx: _lvgl.int32_t, class_p: "obj_class_t") -> "obj":
        return _wrap_obj(_lvgl.obj_get_child_by_type(self, idx, class_p))

    def get_sibling(self, idx: _lvgl.int32_t) -> "obj":
        return _wrap_obj(_lvgl.obj_get_sibling(self, idx))

    def get_sibling_by_type(self, idx: _lvgl.int32_t, class_p: "obj_class_t") -> "obj":
        return _wrap_obj(_lvgl.obj_get_sibling_by_type(self, idx, class_p))

    def get_child_count(self) -> _lvgl.uint32_t:
        return _lvgl.obj_get_child_count(self)

    def get_child_count_by_type(self, class_p: "obj_class_t") -> _lvgl.uint32_t:
        return _lvgl.obj_get_child_count_by_type(self, class_p)

    def get_index(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_index(self)

    def get_index_by_type(self, class_p: "obj_class_t") -> _lvgl.int32_t:
        return _lvgl.obj_get_index_by_type(self, class_p)

    def tree_walk(self, cb: "objree_walk_cb_t", user_data: "Any") -> None:
        return _lvgl.obj_tree_walk(self, cb, user_data)

    def dump_tree(self) -> None:
        return _lvgl.obj_dump_tree(self)

    def set_pos(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_pos(self, x, y)

    def set_x(self, x: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_x(self, x)

    def set_y(self, y: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_y(self, y)

    def set_size(self, w: _lvgl.int32_t, h: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_size(self, w, h)

    def refr_size(self) -> _lvgl._Bool:
        return _lvgl.obj_refr_size(self)

    def set_width(self, w: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_width(self, w)

    def set_height(self, h: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_height(self, h)

    def set_content_width(self, w: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_content_width(self, w)

    def set_content_height(self, h: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_content_height(self, h)

    def set_layout(self, layout: _lvgl.uint32_t) -> None:
        return _lvgl.obj_set_layout(self, layout)

    def is_layout_positioned(self) -> _lvgl._Bool:
        return _lvgl.obj_is_layout_positioned(self)

    def mark_layout_as_dirty(self) -> None:
        return _lvgl.obj_mark_layout_as_dirty(self)

    def update_layout(self) -> None:
        return _lvgl.obj_update_layout(self)

    def set_align(self, align: _lvgl.align_t) -> None:
        return _lvgl.obj_set_align(self, align)

    def align(self, align: _lvgl.align_t, x_ofs: _lvgl.int32_t, y_ofs: _lvgl.int32_t) -> None:
        return _lvgl.obj_align(self, align, x_ofs, y_ofs)

    def align_to(self, base: "obj", align: _lvgl.align_t, x_ofs: _lvgl.int32_t, y_ofs: _lvgl.int32_t) -> None:
        return _lvgl.obj_align_to(self, base, align, x_ofs, y_ofs)

    def center(self) -> None:
        return _lvgl.obj_center(self)

    def set_transform(self, matrix: "matrix_t") -> None:
        return _lvgl.obj_set_transform(self, matrix)

    def reset_transform(self) -> None:
        return _lvgl.obj_reset_transform(self)

    def get_coords(self, coords: "area_t") -> None:
        return _lvgl.obj_get_coords(self, coords)

    def get_x(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_x(self)

    def get_x2(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_x2(self)

    def get_y(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_y(self)

    def get_y2(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_y2(self)

    def get_x_aligned(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_x_aligned(self)

    def get_y_aligned(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_y_aligned(self)

    def get_width(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_width(self)

    def get_height(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_height(self)

    def get_content_width(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_content_width(self)

    def get_content_height(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_content_height(self)

    def get_content_coords(self, area: "area_t") -> None:
        return _lvgl.obj_get_content_coords(self, area)

    def get_self_width(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_self_width(self)

    def get_self_height(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_self_height(self)

    def get_style_clamped_width(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_clamped_width(self)

    def get_style_clamped_height(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_clamped_height(self)

    def is_width_min(self) -> _lvgl._Bool:
        return _lvgl.obj_is_width_min(self)

    def is_height_min(self) -> _lvgl._Bool:
        return _lvgl.obj_is_height_min(self)

    def is_width_max(self) -> _lvgl._Bool:
        return _lvgl.obj_is_width_max(self)

    def is_height_max(self) -> _lvgl._Bool:
        return _lvgl.obj_is_height_max(self)

    def refresh_self_size(self) -> _lvgl._Bool:
        return _lvgl.obj_refresh_self_size(self)

    def refr_pos(self) -> None:
        return _lvgl.obj_refr_pos(self)

    def move_to(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> None:
        return _lvgl.obj_move_to(self, x, y)

    def move_children_by(self, x_diff: _lvgl.int32_t, y_diff: _lvgl.int32_t, ignore_floating: _lvgl._Bool) -> None:
        return _lvgl.obj_move_children_by(self, x_diff, y_diff, ignore_floating)

    def get_transform(self) -> "matrix_t":
        return _lvgl.obj_get_transform(self)

    def transform_point(self, p: _lvgl.point_t, flags: _lvgl.obj_point_transform_flag_t) -> None:
        return _lvgl.obj_transform_point(self, p, flags)

    def transform_point_array(self, points: "List", count: _lvgl.size_t, flags: _lvgl.obj_point_transform_flag_t) -> None:
        return _lvgl.obj_transform_point_array(self, points, count, flags)

    def get_transformed_area(self, area: "area_t", flags: _lvgl.obj_point_transform_flag_t) -> None:
        return _lvgl.obj_get_transformed_area(self, area, flags)

    def invalidate_area(self, area: "area_t") -> _lvgl.result_t:
        return _lvgl.obj_invalidate_area(self, area)

    def invalidate(self) -> _lvgl.result_t:
        return _lvgl.obj_invalidate(self)

    def area_is_visible(self, area: "area_t") -> _lvgl._Bool:
        return _lvgl.obj_area_is_visible(self, area)

    def is_visible(self) -> _lvgl._Bool:
        return _lvgl.obj_is_visible(self)

    def set_ext_click_area(self, size: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_ext_click_area(self, size)

    def get_click_area(self, area: "area_t") -> None:
        return _lvgl.obj_get_click_area(self, area)

    def hit_test(self, point: _lvgl.point_t) -> _lvgl._Bool:
        return _lvgl.obj_hit_test(self, point)

    def calc_dynamic_width(self, prop: _lvgl.style_prop_t) -> _lvgl.int32_t:
        return _lvgl.obj_calc_dynamic_width(self, prop)

    def calc_dynamic_height(self, prop: _lvgl.style_prop_t) -> _lvgl.int32_t:
        return _lvgl.obj_calc_dynamic_height(self, prop)

    def set_scrollbar_mode(self, mode: _lvgl.scrollbar_mode_t) -> None:
        return _lvgl.obj_set_scrollbar_mode(self, mode)

    def set_scroll_dir(self, dir: _lvgl.dir_t) -> None:
        return _lvgl.obj_set_scroll_dir(self, dir)

    def set_scroll_snap_x(self, align: _lvgl.scroll_snap_t) -> None:
        return _lvgl.obj_set_scroll_snap_x(self, align)

    def set_scroll_snap_y(self, align: _lvgl.scroll_snap_t) -> None:
        return _lvgl.obj_set_scroll_snap_y(self, align)

    def get_scrollbar_mode(self) -> _lvgl.scrollbar_mode_t:
        return _lvgl.obj_get_scrollbar_mode(self)

    def get_scroll_dir(self) -> _lvgl.dir_t:
        return _lvgl.obj_get_scroll_dir(self)

    def get_scroll_snap_x(self) -> _lvgl.scroll_snap_t:
        return _lvgl.obj_get_scroll_snap_x(self)

    def get_scroll_snap_y(self) -> _lvgl.scroll_snap_t:
        return _lvgl.obj_get_scroll_snap_y(self)

    def get_scroll_x(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_scroll_x(self)

    def get_scroll_y(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_scroll_y(self)

    def get_scroll_top(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_scroll_top(self)

    def get_scroll_bottom(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_scroll_bottom(self)

    def get_scroll_left(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_scroll_left(self)

    def get_scroll_right(self) -> _lvgl.int32_t:
        return _lvgl.obj_get_scroll_right(self)

    def get_scroll_end(self, end: _lvgl.point_t) -> None:
        return _lvgl.obj_get_scroll_end(self, end)

    def scroll_by(self, dx: _lvgl.int32_t, dy: _lvgl.int32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_by(self, dx, dy, anim_en)

    def scroll_by_bounded(self, dx: _lvgl.int32_t, dy: _lvgl.int32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_by_bounded(self, dx, dy, anim_en)

    def scroll_to(self, x: _lvgl.int32_t, y: _lvgl.int32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_to(self, x, y, anim_en)

    def scroll_to_x(self, x: _lvgl.int32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_to_x(self, x, anim_en)

    def scroll_to_y(self, y: _lvgl.int32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_to_y(self, y, anim_en)

    def scroll_to_view(self, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_to_view(self, anim_en)

    def scroll_to_view_recursive(self, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_scroll_to_view_recursive(self, anim_en)

    def is_scrolling(self) -> _lvgl._Bool:
        return _lvgl.obj_is_scrolling(self)

    def stop_scroll_anim(self) -> None:
        return _lvgl.obj_stop_scroll_anim(self)

    def update_snap(self, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_update_snap(self, anim_en)

    def get_scrollbar_area(self, hor: "area_t", ver: "area_t") -> None:
        return _lvgl.obj_get_scrollbar_area(self, hor, ver)

    def scrollbar_invalidate(self) -> None:
        return _lvgl.obj_scrollbar_invalidate(self)

    def readjust_scroll(self, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.obj_readjust_scroll(self, anim_en)

    def add_style(self, style: "style_t", selector: _lvgl.style_selector_t) -> None:
        _retain_obj_ref(self, 'styles', style, append=True)
        return _lvgl.obj_add_style(self, style, selector)

    def replace_style(self, old_style: "style_t", new_style: "style_t", selector: _lvgl.style_selector_t) -> _lvgl._Bool:
        return _lvgl.obj_replace_style(self, old_style, new_style, selector)

    def remove_style(self, style: "style_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_remove_style(self, style, selector)

    def remove_theme(self, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_remove_theme(self, selector)

    def remove_style_all(self) -> None:
        result = _lvgl.obj_remove_style_all(self)
        _release_obj_refs(self, 'styles')
        return result

    def refresh_style(self, part: _lvgl.part_t, prop: _lvgl.style_prop_t) -> None:
        return _lvgl.obj_refresh_style(self, part, prop)

    def style_set_disabled(self, style: "style_t", selector: _lvgl.style_selector_t, dis: _lvgl._Bool) -> None:
        return _lvgl.obj_style_set_disabled(self, style, selector, dis)

    def style_get_disabled(self, style: "style_t", selector: _lvgl.style_selector_t) -> _lvgl._Bool:
        return _lvgl.obj_style_get_disabled(self, style, selector)

    def get_style_prop(self, part: _lvgl.part_t, prop: _lvgl.style_prop_t) -> "style_value_t":
        return _lvgl.obj_get_style_prop(self, part, prop)

    def has_style_prop(self, selector: _lvgl.style_selector_t, prop: _lvgl.style_prop_t) -> _lvgl._Bool:
        return _lvgl.obj_has_style_prop(self, selector, prop)

    def set_local_style_prop(self, prop: _lvgl.style_prop_t, value: "style_value_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_local_style_prop(self, prop, value, selector)

    def get_local_style_prop(self, prop: _lvgl.style_prop_t, value: "style_value_t", selector: _lvgl.style_selector_t) -> _lvgl.style_res_t:
        return _lvgl.obj_get_local_style_prop(self, prop, value, selector)

    def remove_local_style_prop(self, prop: _lvgl.style_prop_t, selector: _lvgl.style_selector_t) -> _lvgl._Bool:
        return _lvgl.obj_remove_local_style_prop(self, prop, selector)

    def style_apply_color_filter(self, part: _lvgl.part_t, v: "style_value_t") -> "style_value_t":
        return _lvgl.obj_style_apply_color_filter(self, part, v)

    def fade_in(self, time: _lvgl.uint32_t, delay: _lvgl.uint32_t) -> None:
        return _lvgl.obj_fade_in(self, time, delay)

    def fade_out(self, time: _lvgl.uint32_t, delay: _lvgl.uint32_t) -> None:
        return _lvgl.obj_fade_out(self, time, delay)

    def get_style_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_width(self, part)

    def get_style_min_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_min_width(self, part)

    def get_style_max_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_max_width(self, part)

    def get_style_height(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_height(self, part)

    def get_style_min_height(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_min_height(self, part)

    def get_style_max_height(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_max_height(self, part)

    def get_style_length(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_length(self, part)

    def get_style_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_x(self, part)

    def get_style_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_y(self, part)

    def get_style_align(self, part: _lvgl.part_t) -> _lvgl.align_t:
        return _lvgl.obj_get_style_align(self, part)

    def get_style_transform_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_width(self, part)

    def get_style_transform_height(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_height(self, part)

    def get_style_translate_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_translate_x(self, part)

    def get_style_translate_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_translate_y(self, part)

    def get_style_translate_radial(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_translate_radial(self, part)

    def get_style_transform_scale_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_scale_x(self, part)

    def get_style_transform_scale_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_scale_y(self, part)

    def get_style_transform_rotation(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_rotation(self, part)

    def get_style_transform_pivot_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_pivot_x(self, part)

    def get_style_transform_pivot_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_pivot_y(self, part)

    def get_style_transform_skew_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_skew_x(self, part)

    def get_style_transform_skew_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_skew_y(self, part)

    def get_style_pad_top(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_top(self, part)

    def get_style_pad_bottom(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_bottom(self, part)

    def get_style_pad_left(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_left(self, part)

    def get_style_pad_right(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_right(self, part)

    def get_style_pad_row(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_row(self, part)

    def get_style_pad_column(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_column(self, part)

    def get_style_pad_radial(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_pad_radial(self, part)

    def get_style_margin_top(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_margin_top(self, part)

    def get_style_margin_bottom(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_margin_bottom(self, part)

    def get_style_margin_left(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_margin_left(self, part)

    def get_style_margin_right(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_margin_right(self, part)

    def get_style_bg_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_bg_color(self, part)

    def get_style_bg_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_bg_color_filtered(self, part)

    def get_style_bg_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_bg_opa(self, part)

    def get_style_bg_grad_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_bg_grad_color(self, part)

    def get_style_bg_grad_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_bg_grad_color_filtered(self, part)

    def get_style_bg_grad_dir(self, part: _lvgl.part_t) -> _lvgl.grad_dir_t:
        return _lvgl.obj_get_style_bg_grad_dir(self, part)

    def get_style_bg_main_stop(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_bg_main_stop(self, part)

    def get_style_bg_grad_stop(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_bg_grad_stop(self, part)

    def get_style_bg_main_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_bg_main_opa(self, part)

    def get_style_bg_grad_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_bg_grad_opa(self, part)

    def get_style_bg_grad(self, part: _lvgl.part_t) -> "grad_dsc_t":
        return _lvgl.obj_get_style_bg_grad(self, part)

    def get_style_bg_image_src(self, part: _lvgl.part_t) -> "Any":
        return _lvgl.obj_get_style_bg_image_src(self, part)

    def get_style_bg_image_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_bg_image_opa(self, part)

    def get_style_bg_image_recolor(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_bg_image_recolor(self, part)

    def get_style_bg_image_recolor_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_bg_image_recolor_filtered(self, part)

    def get_style_bg_image_recolor_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_bg_image_recolor_opa(self, part)

    def get_style_bg_image_tiled(self, part: _lvgl.part_t) -> _lvgl._Bool:
        return _lvgl.obj_get_style_bg_image_tiled(self, part)

    def get_style_border_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_border_color(self, part)

    def get_style_border_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_border_color_filtered(self, part)

    def get_style_border_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_border_opa(self, part)

    def get_style_border_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_border_width(self, part)

    def get_style_border_side(self, part: _lvgl.part_t) -> _lvgl.border_side_t:
        return _lvgl.obj_get_style_border_side(self, part)

    def get_style_border_post(self, part: _lvgl.part_t) -> _lvgl._Bool:
        return _lvgl.obj_get_style_border_post(self, part)

    def get_style_outline_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_outline_width(self, part)

    def get_style_outline_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_outline_color(self, part)

    def get_style_outline_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_outline_color_filtered(self, part)

    def get_style_outline_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_outline_opa(self, part)

    def get_style_outline_pad(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_outline_pad(self, part)

    def get_style_shadow_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_shadow_width(self, part)

    def get_style_shadow_offset_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_shadow_offset_x(self, part)

    def get_style_shadow_offset_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_shadow_offset_y(self, part)

    def get_style_shadow_spread(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_shadow_spread(self, part)

    def get_style_shadow_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_shadow_color(self, part)

    def get_style_shadow_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_shadow_color_filtered(self, part)

    def get_style_shadow_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_shadow_opa(self, part)

    def get_style_image_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_image_opa(self, part)

    def get_style_image_recolor(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_image_recolor(self, part)

    def get_style_image_recolor_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_image_recolor_filtered(self, part)

    def get_style_image_recolor_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_image_recolor_opa(self, part)

    def get_style_image_colorkey(self, part: _lvgl.part_t) -> _lvgl.image_colorkey_t:
        return _lvgl.obj_get_style_image_colorkey(self, part)

    def get_style_line_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_line_width(self, part)

    def get_style_line_dash_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_line_dash_width(self, part)

    def get_style_line_dash_gap(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_line_dash_gap(self, part)

    def get_style_line_rounded(self, part: _lvgl.part_t) -> _lvgl._Bool:
        return _lvgl.obj_get_style_line_rounded(self, part)

    def get_style_line_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_line_color(self, part)

    def get_style_line_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_line_color_filtered(self, part)

    def get_style_line_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_line_opa(self, part)

    def get_style_arc_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_arc_width(self, part)

    def get_style_arc_rounded(self, part: _lvgl.part_t) -> _lvgl._Bool:
        return _lvgl.obj_get_style_arc_rounded(self, part)

    def get_style_arc_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_arc_color(self, part)

    def get_style_arc_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_arc_color_filtered(self, part)

    def get_style_arc_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_arc_opa(self, part)

    def get_style_arc_image_src(self, part: _lvgl.part_t) -> "Any":
        return _lvgl.obj_get_style_arc_image_src(self, part)

    def get_style_text_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_text_color(self, part)

    def get_style_text_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_text_color_filtered(self, part)

    def get_style_text_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_text_opa(self, part)

    def get_style_text_font(self, part: _lvgl.part_t) -> "font_t":
        return _lvgl.obj_get_style_text_font(self, part)

    def get_style_text_letter_space(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_text_letter_space(self, part)

    def get_style_text_line_space(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_text_line_space(self, part)

    def get_style_text_decor(self, part: _lvgl.part_t) -> _lvgl.text_decor_t:
        return _lvgl.obj_get_style_text_decor(self, part)

    def get_style_text_align(self, part: _lvgl.part_t) -> _lvgl.text_align_t:
        return _lvgl.obj_get_style_text_align(self, part)

    def get_style_text_outline_stroke_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_text_outline_stroke_color(self, part)

    def get_style_text_outline_stroke_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_text_outline_stroke_color_filtered(self, part)

    def get_style_text_outline_stroke_width(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_text_outline_stroke_width(self, part)

    def get_style_text_outline_stroke_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_text_outline_stroke_opa(self, part)

    def get_style_blur_radius(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_blur_radius(self, part)

    def get_style_blur_backdrop(self, part: _lvgl.part_t) -> _lvgl._Bool:
        return _lvgl.obj_get_style_blur_backdrop(self, part)

    def get_style_blur_quality(self, part: _lvgl.part_t) -> _lvgl.blur_quality_t:
        return _lvgl.obj_get_style_blur_quality(self, part)

    def get_style_drop_shadow_radius(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_drop_shadow_radius(self, part)

    def get_style_drop_shadow_offset_x(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_drop_shadow_offset_x(self, part)

    def get_style_drop_shadow_offset_y(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_drop_shadow_offset_y(self, part)

    def get_style_drop_shadow_color(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_drop_shadow_color(self, part)

    def get_style_drop_shadow_color_filtered(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_drop_shadow_color_filtered(self, part)

    def get_style_drop_shadow_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_drop_shadow_opa(self, part)

    def get_style_drop_shadow_quality(self, part: _lvgl.part_t) -> _lvgl.blur_quality_t:
        return _lvgl.obj_get_style_drop_shadow_quality(self, part)

    def get_style_radius(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_radius(self, part)

    def get_style_radial_offset(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_radial_offset(self, part)

    def get_style_clip_corner(self, part: _lvgl.part_t) -> _lvgl._Bool:
        return _lvgl.obj_get_style_clip_corner(self, part)

    def get_style_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_opa(self, part)

    def get_style_opa_layered(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_opa_layered(self, part)

    def get_style_color_filter_dsc(self, part: _lvgl.part_t) -> "color_filter_dsc_t":
        return _lvgl.obj_get_style_color_filter_dsc(self, part)

    def get_style_color_filter_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_color_filter_opa(self, part)

    def get_style_recolor(self, part: _lvgl.part_t) -> "color_t":
        return _lvgl.obj_get_style_recolor(self, part)

    def get_style_recolor_opa(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_recolor_opa(self, part)

    def get_style_anim(self, part: _lvgl.part_t) -> "anim_t":
        return _lvgl.obj_get_style_anim(self, part)

    def get_style_anim_duration(self, part: _lvgl.part_t) -> _lvgl.uint32_t:
        return _lvgl.obj_get_style_anim_duration(self, part)

    def get_style_transition(self, part: _lvgl.part_t) -> "style_transition_dsc_t":
        return _lvgl.obj_get_style_transition(self, part)

    def get_style_blend_mode(self, part: _lvgl.part_t) -> _lvgl.blend_mode_t:
        return _lvgl.obj_get_style_blend_mode(self, part)

    def get_style_layout(self, part: _lvgl.part_t) -> _lvgl.uint16_t:
        return _lvgl.obj_get_style_layout(self, part)

    def get_style_base_dir(self, part: _lvgl.part_t) -> _lvgl.base_dir_t:
        return _lvgl.obj_get_style_base_dir(self, part)

    def get_style_bitmap_mask_src(self, part: _lvgl.part_t) -> "Any":
        return _lvgl.obj_get_style_bitmap_mask_src(self, part)

    def get_style_rotary_sensitivity(self, part: _lvgl.part_t) -> _lvgl.uint32_t:
        return _lvgl.obj_get_style_rotary_sensitivity(self, part)

    def get_style_flex_flow(self, part: _lvgl.part_t) -> _lvgl.flex_flow_t:
        return _lvgl.obj_get_style_flex_flow(self, part)

    def get_style_flex_main_place(self, part: _lvgl.part_t) -> _lvgl.flex_align_t:
        return _lvgl.obj_get_style_flex_main_place(self, part)

    def get_style_flex_cross_place(self, part: _lvgl.part_t) -> _lvgl.flex_align_t:
        return _lvgl.obj_get_style_flex_cross_place(self, part)

    def get_style_flex_track_place(self, part: _lvgl.part_t) -> _lvgl.flex_align_t:
        return _lvgl.obj_get_style_flex_track_place(self, part)

    def get_style_flex_grow(self, part: _lvgl.part_t) -> _lvgl.uint8_t:
        return _lvgl.obj_get_style_flex_grow(self, part)

    def get_style_grid_column_dsc_array(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_grid_column_dsc_array(self, part)

    def get_style_grid_column_align(self, part: _lvgl.part_t) -> _lvgl.grid_align_t:
        return _lvgl.obj_get_style_grid_column_align(self, part)

    def get_style_grid_row_dsc_array(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_grid_row_dsc_array(self, part)

    def get_style_grid_row_align(self, part: _lvgl.part_t) -> _lvgl.grid_align_t:
        return _lvgl.obj_get_style_grid_row_align(self, part)

    def get_style_grid_cell_column_pos(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_grid_cell_column_pos(self, part)

    def get_style_grid_cell_x_align(self, part: _lvgl.part_t) -> _lvgl.grid_align_t:
        return _lvgl.obj_get_style_grid_cell_x_align(self, part)

    def get_style_grid_cell_column_span(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_grid_cell_column_span(self, part)

    def get_style_grid_cell_row_pos(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_grid_cell_row_pos(self, part)

    def get_style_grid_cell_y_align(self, part: _lvgl.part_t) -> _lvgl.grid_align_t:
        return _lvgl.obj_get_style_grid_cell_y_align(self, part)

    def get_style_grid_cell_row_span(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_grid_cell_row_span(self, part)

    def set_style_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_width(self, value, selector)

    def set_style_min_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_min_width(self, value, selector)

    def set_style_max_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_max_width(self, value, selector)

    def set_style_height(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_height(self, value, selector)

    def set_style_min_height(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_min_height(self, value, selector)

    def set_style_max_height(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_max_height(self, value, selector)

    def set_style_length(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_length(self, value, selector)

    def set_style_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_x(self, value, selector)

    def set_style_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_y(self, value, selector)

    def set_style_align(self, value: _lvgl.align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_align(self, value, selector)

    def set_style_transform_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_width(self, value, selector)

    def set_style_transform_height(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_height(self, value, selector)

    def set_style_translate_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_translate_x(self, value, selector)

    def set_style_translate_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_translate_y(self, value, selector)

    def set_style_translate_radial(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_translate_radial(self, value, selector)

    def set_style_transform_scale_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_scale_x(self, value, selector)

    def set_style_transform_scale_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_scale_y(self, value, selector)

    def set_style_transform_rotation(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_rotation(self, value, selector)

    def set_style_transform_pivot_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_pivot_x(self, value, selector)

    def set_style_transform_pivot_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_pivot_y(self, value, selector)

    def set_style_transform_skew_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_skew_x(self, value, selector)

    def set_style_transform_skew_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_skew_y(self, value, selector)

    def set_style_pad_top(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_top(self, value, selector)

    def set_style_pad_bottom(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_bottom(self, value, selector)

    def set_style_pad_left(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_left(self, value, selector)

    def set_style_pad_right(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_right(self, value, selector)

    def set_style_pad_row(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_row(self, value, selector)

    def set_style_pad_column(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_column(self, value, selector)

    def set_style_pad_radial(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_radial(self, value, selector)

    def set_style_margin_top(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_top(self, value, selector)

    def set_style_margin_bottom(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_bottom(self, value, selector)

    def set_style_margin_left(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_left(self, value, selector)

    def set_style_margin_right(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_right(self, value, selector)

    def set_style_bg_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_color(self, value, selector)

    def set_style_bg_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_opa(self, value, selector)

    def set_style_bg_grad_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_grad_color(self, value, selector)

    def set_style_bg_grad_dir(self, value: _lvgl.grad_dir_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_grad_dir(self, value, selector)

    def set_style_bg_main_stop(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_main_stop(self, value, selector)

    def set_style_bg_grad_stop(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_grad_stop(self, value, selector)

    def set_style_bg_main_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_main_opa(self, value, selector)

    def set_style_bg_grad_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_grad_opa(self, value, selector)

    def set_style_bg_grad(self, value: "grad_dsc_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_grad(self, value, selector)

    def set_style_bg_image_src(self, value: None, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_image_src(self, value, selector)

    def set_style_bg_image_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_image_opa(self, value, selector)

    def set_style_bg_image_recolor(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_image_recolor(self, value, selector)

    def set_style_bg_image_recolor_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_image_recolor_opa(self, value, selector)

    def set_style_bg_image_tiled(self, value: _lvgl._Bool, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bg_image_tiled(self, value, selector)

    def set_style_border_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_border_color(self, value, selector)

    def set_style_border_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_border_opa(self, value, selector)

    def set_style_border_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_border_width(self, value, selector)

    def set_style_border_side(self, value: _lvgl.border_side_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_border_side(self, value, selector)

    def set_style_border_post(self, value: _lvgl._Bool, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_border_post(self, value, selector)

    def set_style_outline_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_outline_width(self, value, selector)

    def set_style_outline_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_outline_color(self, value, selector)

    def set_style_outline_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_outline_opa(self, value, selector)

    def set_style_outline_pad(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_outline_pad(self, value, selector)

    def set_style_shadow_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_shadow_width(self, value, selector)

    def set_style_shadow_offset_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_shadow_offset_x(self, value, selector)

    def set_style_shadow_offset_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_shadow_offset_y(self, value, selector)

    def set_style_shadow_spread(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_shadow_spread(self, value, selector)

    def set_style_shadow_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_shadow_color(self, value, selector)

    def set_style_shadow_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_shadow_opa(self, value, selector)

    def set_style_image_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_image_opa(self, value, selector)

    def set_style_image_recolor(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_image_recolor(self, value, selector)

    def set_style_image_recolor_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_image_recolor_opa(self, value, selector)

    def set_style_image_colorkey(self, value: _lvgl.image_colorkey_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_image_colorkey(self, value, selector)

    def set_style_line_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_line_width(self, value, selector)

    def set_style_line_dash_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_line_dash_width(self, value, selector)

    def set_style_line_dash_gap(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_line_dash_gap(self, value, selector)

    def set_style_line_rounded(self, value: _lvgl._Bool, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_line_rounded(self, value, selector)

    def set_style_line_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_line_color(self, value, selector)

    def set_style_line_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_line_opa(self, value, selector)

    def set_style_arc_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_arc_width(self, value, selector)

    def set_style_arc_rounded(self, value: _lvgl._Bool, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_arc_rounded(self, value, selector)

    def set_style_arc_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_arc_color(self, value, selector)

    def set_style_arc_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_arc_opa(self, value, selector)

    def set_style_arc_image_src(self, value: None, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_arc_image_src(self, value, selector)

    def set_style_text_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_color(self, value, selector)

    def set_style_text_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_opa(self, value, selector)

    def set_style_text_font(self, value: "font_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_font(self, value, selector)

    def set_style_text_letter_space(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_letter_space(self, value, selector)

    def set_style_text_line_space(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_line_space(self, value, selector)

    def set_style_text_decor(self, value: _lvgl.text_decor_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_decor(self, value, selector)

    def set_style_text_align(self, value: _lvgl.text_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_align(self, value, selector)

    def set_style_text_outline_stroke_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_outline_stroke_color(self, value, selector)

    def set_style_text_outline_stroke_width(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_outline_stroke_width(self, value, selector)

    def set_style_text_outline_stroke_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_text_outline_stroke_opa(self, value, selector)

    def set_style_blur_radius(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_blur_radius(self, value, selector)

    def set_style_blur_backdrop(self, value: _lvgl._Bool, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_blur_backdrop(self, value, selector)

    def set_style_blur_quality(self, value: _lvgl.blur_quality_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_blur_quality(self, value, selector)

    def set_style_drop_shadow_radius(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_drop_shadow_radius(self, value, selector)

    def set_style_drop_shadow_offset_x(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_drop_shadow_offset_x(self, value, selector)

    def set_style_drop_shadow_offset_y(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_drop_shadow_offset_y(self, value, selector)

    def set_style_drop_shadow_color(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_drop_shadow_color(self, value, selector)

    def set_style_drop_shadow_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_drop_shadow_opa(self, value, selector)

    def set_style_drop_shadow_quality(self, value: _lvgl.blur_quality_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_drop_shadow_quality(self, value, selector)

    def set_style_radius(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_radius(self, value, selector)

    def set_style_radial_offset(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_radial_offset(self, value, selector)

    def set_style_clip_corner(self, value: _lvgl._Bool, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_clip_corner(self, value, selector)

    def set_style_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_opa(self, value, selector)

    def set_style_opa_layered(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_opa_layered(self, value, selector)

    def set_style_color_filter_dsc(self, value: "color_filter_dsc_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_color_filter_dsc(self, value, selector)

    def set_style_color_filter_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_color_filter_opa(self, value, selector)

    def set_style_recolor(self, value: "color_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_recolor(self, value, selector)

    def set_style_recolor_opa(self, value: _lvgl.opa_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_recolor_opa(self, value, selector)

    def set_style_anim(self, value: "anim_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_anim(self, value, selector)

    def set_style_anim_duration(self, value: _lvgl.uint32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_anim_duration(self, value, selector)

    def set_style_transition(self, value: "style_transition_dsc_t", selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transition(self, value, selector)

    def set_style_blend_mode(self, value: _lvgl.blend_mode_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_blend_mode(self, value, selector)

    def set_style_layout(self, value: _lvgl.uint16_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_layout(self, value, selector)

    def set_style_base_dir(self, value: _lvgl.base_dir_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_base_dir(self, value, selector)

    def set_style_bitmap_mask_src(self, value: None, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_bitmap_mask_src(self, value, selector)

    def set_style_rotary_sensitivity(self, value: _lvgl.uint32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_rotary_sensitivity(self, value, selector)

    def set_style_flex_flow(self, value: _lvgl.flex_flow_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_flex_flow(self, value, selector)

    def set_style_flex_main_place(self, value: _lvgl.flex_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_flex_main_place(self, value, selector)

    def set_style_flex_cross_place(self, value: _lvgl.flex_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_flex_cross_place(self, value, selector)

    def set_style_flex_track_place(self, value: _lvgl.flex_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_flex_track_place(self, value, selector)

    def set_style_flex_grow(self, value: _lvgl.uint8_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_flex_grow(self, value, selector)

    def set_style_grid_column_dsc_array(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_column_dsc_array(self, value, selector)

    def set_style_grid_column_align(self, value: _lvgl.grid_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_column_align(self, value, selector)

    def set_style_grid_row_dsc_array(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_row_dsc_array(self, value, selector)

    def set_style_grid_row_align(self, value: _lvgl.grid_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_row_align(self, value, selector)

    def set_style_grid_cell_column_pos(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_cell_column_pos(self, value, selector)

    def set_style_grid_cell_x_align(self, value: _lvgl.grid_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_cell_x_align(self, value, selector)

    def set_style_grid_cell_column_span(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_cell_column_span(self, value, selector)

    def set_style_grid_cell_row_pos(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_cell_row_pos(self, value, selector)

    def set_style_grid_cell_y_align(self, value: _lvgl.grid_align_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_cell_y_align(self, value, selector)

    def set_style_grid_cell_row_span(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_grid_cell_row_span(self, value, selector)

    def set_style_pad_all(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_all(self, value, selector)

    def set_style_pad_hor(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_hor(self, value, selector)

    def set_style_pad_ver(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_ver(self, value, selector)

    def set_style_margin_all(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_all(self, value, selector)

    def set_style_margin_hor(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_hor(self, value, selector)

    def set_style_margin_ver(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_margin_ver(self, value, selector)

    def set_style_pad_gap(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_pad_gap(self, value, selector)

    def set_style_size(self, width: _lvgl.int32_t, height: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_size(self, width, height, selector)

    def set_style_transform_scale(self, value: _lvgl.int32_t, selector: _lvgl.style_selector_t) -> None:
        return _lvgl.obj_set_style_transform_scale(self, value, selector)

    def get_style_space_left(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_space_left(self, part)

    def get_style_space_right(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_space_right(self, part)

    def get_style_space_top(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_space_top(self, part)

    def get_style_space_bottom(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_space_bottom(self, part)

    def calculate_style_text_align(self, part: _lvgl.part_t, txt: _lvgl.char) -> _lvgl.text_align_t:
        return _lvgl.obj_calculate_style_text_align(self, part, txt)

    def get_style_transform_scale_x_safe(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_scale_x_safe(self, part)

    def get_style_transform_scale_y_safe(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_get_style_transform_scale_y_safe(self, part)

    def get_style_opa_recursive(self, part: _lvgl.part_t) -> _lvgl.opa_t:
        return _lvgl.obj_get_style_opa_recursive(self, part)

    def style_apply_recolor(self, part: _lvgl.part_t, color: "color32_t") -> "color32_t":
        return _lvgl.obj_style_apply_recolor(self, part, color)

    def get_style_recolor_recursive(self, part: _lvgl.part_t) -> "color32_t":
        return _lvgl.obj_get_style_recolor_recursive(self, part)

    def bind_style(self, style: "style_t", selector: _lvgl.style_selector_t, subject: "subject_t", ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_style(self, style, selector, subject, ref_value)

    def bind_style_prop(self, prop: _lvgl.style_prop_t, selector: _lvgl.style_selector_t, subject: "subject_t") -> "observer_t":
        return _lvgl.obj_bind_style_prop(self, prop, selector, subject)

    def init_draw_rect_dsc(self, part: _lvgl.part_t, draw_dsc: "draw_rect_dsc_t") -> None:
        return _lvgl.obj_init_draw_rect_dsc(self, part, draw_dsc)

    def init_draw_label_dsc(self, part: _lvgl.part_t, draw_dsc: "draw_label_dsc_t") -> None:
        return _lvgl.obj_init_draw_label_dsc(self, part, draw_dsc)

    def init_draw_image_dsc(self, part: _lvgl.part_t, draw_dsc: "draw_image_dsc_t") -> None:
        return _lvgl.obj_init_draw_image_dsc(self, part, draw_dsc)

    def init_draw_line_dsc(self, part: _lvgl.part_t, draw_dsc: "draw_line_dsc_t") -> None:
        return _lvgl.obj_init_draw_line_dsc(self, part, draw_dsc)

    def init_draw_arc_dsc(self, part: _lvgl.part_t, draw_dsc: "draw_arc_dsc_t") -> None:
        return _lvgl.obj_init_draw_arc_dsc(self, part, draw_dsc)

    def init_draw_blur_dsc(self, part: _lvgl.part_t, draw_dsc: "draw_blur_dsc_t") -> None:
        return _lvgl.obj_init_draw_blur_dsc(self, part, draw_dsc)

    def calculate_ext_draw_size(self, part: _lvgl.part_t) -> _lvgl.int32_t:
        return _lvgl.obj_calculate_ext_draw_size(self, part)

    def refresh_ext_draw_size(self) -> None:
        return _lvgl.obj_refresh_ext_draw_size(self)

    def class_init_obj(self) -> None:
        return _lvgl.obj_class_init_obj(self)

    def is_editable(self) -> _lvgl._Bool:
        return _lvgl.obj_is_editable(self)

    def is_group_def(self) -> _lvgl._Bool:
        return _lvgl.obj_is_group_def(self)

    def send_event(self, event_code: _lvgl.event_code_t, param: None) -> _lvgl.result_t:
        return _lvgl.obj_send_event(self, event_code, param)

    def add_event_cb(self, event_cb: "event_cb_t", filter: _lvgl.event_code_t, user_data: "Any") -> "event_dsc_t":
        return _lvgl.obj_add_event_cb(self, event_cb, filter, user_data)

    def get_event_count(self) -> _lvgl.uint32_t:
        return _lvgl.obj_get_event_count(self)

    def get_event_dsc(self, index: _lvgl.uint32_t) -> "event_dsc_t":
        return _lvgl.obj_get_event_dsc(self, index)

    def remove_event(self, index: _lvgl.uint32_t) -> _lvgl._Bool:
        dsc = _lvgl.obj_get_event_dsc(self, index)
        callback_ref = _event_callback_ref(dsc)
        result = _lvgl.obj_remove_event(self, index)
        if result:
            _release_event_callback_ref(callback_ref)
        return result

    def remove_event_dsc(self, dsc: "event_dsc_t") -> _lvgl._Bool:
        callback_ref = _event_callback_ref(dsc)
        result = _lvgl.obj_remove_event_dsc(self, dsc)
        if result:
            _release_event_callback_ref(callback_ref)
        return result

    def remove_event_cb(self, event_cb: "event_cb_t") -> _lvgl.uint32_t:
        return _lvgl.obj_remove_event_cb(self, event_cb)

    def remove_event_cb_with_user_data(self, event_cb: "event_cb_t", user_data: "Any") -> _lvgl.uint32_t:
        return _lvgl.obj_remove_event_cb_with_user_data(self, event_cb, user_data)

    def add_flag(self, f: _lvgl.obj_flag_t) -> None:
        return _lvgl.obj_add_flag(self, f)

    def remove_flag(self, f: _lvgl.obj_flag_t) -> None:
        return _lvgl.obj_remove_flag(self, f)

    def set_flag(self, f: _lvgl.obj_flag_t, v: _lvgl._Bool) -> None:
        return _lvgl.obj_set_flag(self, f, v)

    def add_state(self, state: _lvgl.state_t) -> None:
        return _lvgl.obj_add_state(self, state)

    def remove_state(self, state: _lvgl.state_t) -> None:
        return _lvgl.obj_remove_state(self, state)

    def set_state(self, state: _lvgl.state_t, v: _lvgl._Bool) -> None:
        return _lvgl.obj_set_state(self, state, v)

    def set_user_data(self, user_data: "Any") -> None:
        return _lvgl.obj_set_user_data(self, user_data)

    def set_radio_button(self, en: _lvgl._Bool) -> None:
        return _lvgl.obj_set_radio_button(self, en)

    def has_flag(self, f: _lvgl.obj_flag_t) -> _lvgl._Bool:
        return _lvgl.obj_has_flag(self, f)

    def has_flag_any(self, f: _lvgl.obj_flag_t) -> _lvgl._Bool:
        return _lvgl.obj_has_flag_any(self, f)

    def get_state(self) -> _lvgl.state_t:
        return _lvgl.obj_get_state(self)

    def has_state(self, state: _lvgl.state_t) -> _lvgl._Bool:
        return _lvgl.obj_has_state(self, state)

    def is_radio_button(self) -> _lvgl._Bool:
        return _lvgl.obj_is_radio_button(self)

    def get_group(self) -> "group_t":
        return _lvgl.obj_get_group(self)

    def get_user_data(self) -> "Any":
        return _lvgl.obj_get_user_data(self)

    def allocate_spec_attr(self) -> None:
        return _lvgl.obj_allocate_spec_attr(self)

    def check_type(self, class_p: "obj_class_t") -> _lvgl._Bool:
        return _lvgl.obj_check_type(self, class_p)

    def has_class(self, class_p: "obj_class_t") -> _lvgl._Bool:
        return _lvgl.obj_has_class(self, class_p)

    def get_class(self) -> "obj_class_t":
        return _lvgl.obj_get_class(self)

    def is_valid(self) -> _lvgl._Bool:
        return _lvgl.obj_is_valid(self)

    def null_on_delete(self) -> None:
        return _lvgl.obj_null_on_delete(self)

    def add_screen_load_event(self, trigger: _lvgl.event_code_t, screen: "obj", anim_type: _lvgl.screen_load_anim_t, duration: _lvgl.uint32_t, delay: _lvgl.uint32_t) -> None:
        return _lvgl.obj_add_screen_load_event(self, trigger, screen, anim_type, duration, delay)

    def add_screen_create_event(self, trigger: _lvgl.event_code_t, screen_create_cb: "screen_create_cb_t", anim_type: _lvgl.screen_load_anim_t, duration: _lvgl.uint32_t, delay: _lvgl.uint32_t) -> None:
        return _lvgl.obj_add_screen_create_event(self, trigger, screen_create_cb, anim_type, duration, delay)

    def add_play_timeline_event(self, trigger: _lvgl.event_code_t, at: "anim_timeline_t", delay: _lvgl.uint32_t, reverse: _lvgl._Bool) -> None:
        return _lvgl.obj_add_play_timeline_event(self, trigger, at, delay, reverse)

    def remove_from_subject(self, subject: "subject_t") -> None:
        return _lvgl.obj_remove_from_subject(self, subject)

    def add_subject_increment_event(self, subject: "subject_t", trigger: _lvgl.event_code_t, step: _lvgl.int32_t) -> "subject_increment_dsc_t":
        return _lvgl.obj_add_subject_increment_event(self, subject, trigger, step)

    def set_subject_increment_event_min_value(self, dsc: "subject_increment_dsc_t", min_value: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_subject_increment_event_min_value(self, dsc, min_value)

    def set_subject_increment_event_max_value(self, dsc: "subject_increment_dsc_t", max_value: _lvgl.int32_t) -> None:
        return _lvgl.obj_set_subject_increment_event_max_value(self, dsc, max_value)

    def set_subject_increment_event_rollover(self, dsc: "subject_increment_dsc_t", rollover: _lvgl._Bool) -> None:
        return _lvgl.obj_set_subject_increment_event_rollover(self, dsc, rollover)

    def add_subject_toggle_event(self, subject: "subject_t", trigger: _lvgl.event_code_t) -> None:
        return _lvgl.obj_add_subject_toggle_event(self, subject, trigger)

    def add_subject_set_int_event(self, subject: "subject_t", trigger: _lvgl.event_code_t, value: _lvgl.int32_t) -> None:
        return _lvgl.obj_add_subject_set_int_event(self, subject, trigger, value)

    def add_subject_set_string_event(self, subject: "subject_t", trigger: _lvgl.event_code_t, value: _lvgl.char) -> None:
        return _lvgl.obj_add_subject_set_string_event(self, subject, trigger, value)

    def bind_flag_if_eq(self, subject: "subject_t", flag: _lvgl.obj_flag_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_flag_if_eq(self, subject, flag, ref_value)

    def bind_flag_if_not_eq(self, subject: "subject_t", flag: _lvgl.obj_flag_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_flag_if_not_eq(self, subject, flag, ref_value)

    def bind_flag_if_gt(self, subject: "subject_t", flag: _lvgl.obj_flag_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_flag_if_gt(self, subject, flag, ref_value)

    def bind_flag_if_ge(self, subject: "subject_t", flag: _lvgl.obj_flag_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_flag_if_ge(self, subject, flag, ref_value)

    def bind_flag_if_lt(self, subject: "subject_t", flag: _lvgl.obj_flag_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_flag_if_lt(self, subject, flag, ref_value)

    def bind_flag_if_le(self, subject: "subject_t", flag: _lvgl.obj_flag_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_flag_if_le(self, subject, flag, ref_value)

    def bind_state_if_eq(self, subject: "subject_t", state: _lvgl.state_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_state_if_eq(self, subject, state, ref_value)

    def bind_state_if_not_eq(self, subject: "subject_t", state: _lvgl.state_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_state_if_not_eq(self, subject, state, ref_value)

    def bind_state_if_gt(self, subject: "subject_t", state: _lvgl.state_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_state_if_gt(self, subject, state, ref_value)

    def bind_state_if_ge(self, subject: "subject_t", state: _lvgl.state_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_state_if_ge(self, subject, state, ref_value)

    def bind_state_if_lt(self, subject: "subject_t", state: _lvgl.state_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_state_if_lt(self, subject, state, ref_value)

    def bind_state_if_le(self, subject: "subject_t", state: _lvgl.state_t, ref_value: _lvgl.int32_t) -> "observer_t":
        return _lvgl.obj_bind_state_if_le(self, subject, state, ref_value)

    def bind_checked(self, subject: "subject_t") -> "observer_t":
        return _lvgl.obj_bind_checked(self, subject)

    def move_foreground(self) -> None:
        return _lvgl.obj_move_foreground(self)

    def move_background(self) -> None:
        return _lvgl.obj_move_background(self)


class image(obj):
    
    class ALIGN_BOTTOM:
        LEFT = _lvgl.IMAGE_ALIGN_BOTTOM_LEFT
        MID = _lvgl.IMAGE_ALIGN_BOTTOM_MID
        RIGHT = _lvgl.IMAGE_ALIGN_BOTTOM_RIGHT
        CENTER = _lvgl.IMAGE_ALIGN_CENTER
        CONTAIN = _lvgl.IMAGE_ALIGN_CONTAIN
        COVER = _lvgl.IMAGE_ALIGN_COVER
        DEFAULT = _lvgl.IMAGE_ALIGN_DEFAULT
        LEFT_MID = _lvgl.IMAGE_ALIGN_LEFT_MID
        RIGHT_MID = _lvgl.IMAGE_ALIGN_RIGHT_MID
        STRETCH = _lvgl.IMAGE_ALIGN_STRETCH
        TILE = _lvgl.IMAGE_ALIGN_TILE
        TOP_LEFT = _lvgl.IMAGE_ALIGN_TOP_LEFT
        TOP_MID = _lvgl.IMAGE_ALIGN_TOP_MID
        TOP_RIGHT = _lvgl.IMAGE_ALIGN_TOP_RIGHT
    
    class COMPRESS:
        LZ4 = _lvgl.IMAGE_COMPRESS_LZ4
        NONE = _lvgl.IMAGE_COMPRESS_NONE
        RLE = _lvgl.IMAGE_COMPRESS_RLE
    
    class SRC:
        FILE = _lvgl.IMAGE_SRC_FILE
        SYMBOL = _lvgl.IMAGE_SRC_SYMBOL
        UNKNOWN = _lvgl.IMAGE_SRC_UNKNOWN
        VARIABLE = _lvgl.IMAGE_SRC_VARIABLE

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.image_create(parent)
            cls.cast(self)


    def set_src(self, src: None) -> None:
        return _lvgl.image_set_src(self, src)

    def set_offset_x(self, x: _lvgl.int32_t) -> None:
        return _lvgl.image_set_offset_x(self, x)

    def set_offset_y(self, y: _lvgl.int32_t) -> None:
        return _lvgl.image_set_offset_y(self, y)

    def set_rotation(self, angle: _lvgl.int32_t) -> None:
        return _lvgl.image_set_rotation(self, angle)

    def set_pivot(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> None:
        return _lvgl.image_set_pivot(self, x, y)

    def set_pivot_x(self, x: _lvgl.int32_t) -> None:
        return _lvgl.image_set_pivot_x(self, x)

    def set_pivot_y(self, y: _lvgl.int32_t) -> None:
        return _lvgl.image_set_pivot_y(self, y)

    def set_scale(self, zoom: _lvgl.uint32_t) -> None:
        return _lvgl.image_set_scale(self, zoom)

    def set_scale_x(self, zoom: _lvgl.uint32_t) -> None:
        return _lvgl.image_set_scale_x(self, zoom)

    def set_scale_y(self, zoom: _lvgl.uint32_t) -> None:
        return _lvgl.image_set_scale_y(self, zoom)

    def set_blend_mode(self, blend_mode: _lvgl.blend_mode_t) -> None:
        return _lvgl.image_set_blend_mode(self, blend_mode)

    def set_antialias(self, antialias: _lvgl._Bool) -> None:
        return _lvgl.image_set_antialias(self, antialias)

    def set_inner_align(self, align: _lvgl.image_align_t) -> None:
        return _lvgl.image_set_inner_align(self, align)

    def set_bitmap_map_src(self, src: "image_dsc_t") -> None:
        return _lvgl.image_set_bitmap_map_src(self, src)

    def get_src(self) -> "Any":
        return _lvgl.image_get_src(self)

    def get_offset_x(self) -> _lvgl.int32_t:
        return _lvgl.image_get_offset_x(self)

    def get_offset_y(self) -> _lvgl.int32_t:
        return _lvgl.image_get_offset_y(self)

    def get_rotation(self) -> _lvgl.int32_t:
        return _lvgl.image_get_rotation(self)

    def get_pivot(self, pivot: _lvgl.point_t) -> None:
        return _lvgl.image_get_pivot(self, pivot)

    def get_scale(self) -> _lvgl.int32_t:
        return _lvgl.image_get_scale(self)

    def get_scale_x(self) -> _lvgl.int32_t:
        return _lvgl.image_get_scale_x(self)

    def get_scale_y(self) -> _lvgl.int32_t:
        return _lvgl.image_get_scale_y(self)

    def get_src_width(self) -> _lvgl.int32_t:
        return _lvgl.image_get_src_width(self)

    def get_src_height(self) -> _lvgl.int32_t:
        return _lvgl.image_get_src_height(self)

    def get_transformed_width(self) -> _lvgl.int32_t:
        return _lvgl.image_get_transformed_width(self)

    def get_transformed_height(self) -> _lvgl.int32_t:
        return _lvgl.image_get_transformed_height(self)

    def get_blend_mode(self) -> _lvgl.blend_mode_t:
        return _lvgl.image_get_blend_mode(self)

    def get_antialias(self) -> _lvgl._Bool:
        return _lvgl.image_get_antialias(self)

    def get_inner_align(self) -> _lvgl.image_align_t:
        return _lvgl.image_get_inner_align(self)

    def get_bitmap_map_src(self) -> "image_dsc_t":
        return _lvgl.image_get_bitmap_map_src(self)

    def bind_src(self, subject: "subject_t") -> "observer_t":
        return _lvgl.image_bind_src(self, subject)


class animimg(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.animimg_create(parent)
            cls.cast(self)


    def set_src(self, dsc: "List", num: _lvgl.size_t) -> None:
        return _lvgl.animimg_set_src(self, dsc, num)

    def set_src_reverse(self, dsc: "List", num: _lvgl.size_t) -> None:
        return _lvgl.animimg_set_src_reverse(self, dsc, num)

    def start(self) -> None:
        return _lvgl.animimg_start(self)

    def delete(self) -> _lvgl._Bool:
        return _lvgl.animimg_delete(self)

    def set_duration(self, duration: _lvgl.uint32_t) -> None:
        return _lvgl.animimg_set_duration(self, duration)

    def set_repeat_count(self, count: _lvgl.uint32_t) -> None:
        return _lvgl.animimg_set_repeat_count(self, count)

    def set_reverse_duration(self, duration: _lvgl.uint32_t) -> None:
        return _lvgl.animimg_set_reverse_duration(self, duration)

    def set_reverse_delay(self, duration: _lvgl.uint32_t) -> None:
        return _lvgl.animimg_set_reverse_delay(self, duration)

    def set_start_cb(self, start_cb: "anim_start_cb_t") -> None:
        return _lvgl.animimg_set_start_cb(self, start_cb)

    def set_completed_cb(self, completed_cb: "anim_completed_cb_t") -> None:
        return _lvgl.animimg_set_completed_cb(self, completed_cb)

    def get_src(self) -> "Any":
        return _lvgl.animimg_get_src(self)

    def get_src_count(self) -> _lvgl.uint8_t:
        return _lvgl.animimg_get_src_count(self)

    def get_duration(self) -> _lvgl.uint32_t:
        return _lvgl.animimg_get_duration(self)

    def get_repeat_count(self) -> _lvgl.uint32_t:
        return _lvgl.animimg_get_repeat_count(self)

    def get_anim(self) -> "anim_t":
        return _lvgl.animimg_get_anim(self)


class arc(obj):
    
    class MODE:
        NORMAL = _lvgl.ARC_MODE_NORMAL
        REVERSE = _lvgl.ARC_MODE_REVERSE
        SYMMETRICAL = _lvgl.ARC_MODE_SYMMETRICAL

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.arc_create(parent)
            cls.cast(self)


    def set_start_angle(self, start: _lvgl.value_precise_t) -> None:
        return _lvgl.arc_set_start_angle(self, start)

    def set_end_angle(self, end: _lvgl.value_precise_t) -> None:
        return _lvgl.arc_set_end_angle(self, end)

    def set_angles(self, start: _lvgl.value_precise_t, end: _lvgl.value_precise_t) -> None:
        return _lvgl.arc_set_angles(self, start, end)

    def set_bg_start_angle(self, start: _lvgl.value_precise_t) -> None:
        return _lvgl.arc_set_bg_start_angle(self, start)

    def set_bg_end_angle(self, end: _lvgl.value_precise_t) -> None:
        return _lvgl.arc_set_bg_end_angle(self, end)

    def set_bg_angles(self, start: _lvgl.value_precise_t, end: _lvgl.value_precise_t) -> None:
        return _lvgl.arc_set_bg_angles(self, start, end)

    def set_rotation(self, rotation: _lvgl.int32_t) -> None:
        return _lvgl.arc_set_rotation(self, rotation)

    def set_mode(self, type: _lvgl.arc_mode_t) -> None:
        return _lvgl.arc_set_mode(self, type)

    def set_value(self, value: _lvgl.int32_t) -> None:
        return _lvgl.arc_set_value(self, value)

    def set_range(self, min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.arc_set_range(self, min, max)

    def set_min_value(self, min: _lvgl.int32_t) -> None:
        return _lvgl.arc_set_min_value(self, min)

    def set_max_value(self, max: _lvgl.int32_t) -> None:
        return _lvgl.arc_set_max_value(self, max)

    def set_change_rate(self, rate: _lvgl.uint32_t) -> None:
        return _lvgl.arc_set_change_rate(self, rate)

    def set_knob_offset(self, offset: _lvgl.int32_t) -> None:
        return _lvgl.arc_set_knob_offset(self, offset)

    def get_angle_start(self) -> _lvgl.value_precise_t:
        return _lvgl.arc_get_angle_start(self)

    def get_angle_end(self) -> _lvgl.value_precise_t:
        return _lvgl.arc_get_angle_end(self)

    def get_bg_angle_start(self) -> _lvgl.value_precise_t:
        return _lvgl.arc_get_bg_angle_start(self)

    def get_bg_angle_end(self) -> _lvgl.value_precise_t:
        return _lvgl.arc_get_bg_angle_end(self)

    def get_value(self) -> _lvgl.int32_t:
        return _lvgl.arc_get_value(self)

    def get_min_value(self) -> _lvgl.int32_t:
        return _lvgl.arc_get_min_value(self)

    def get_max_value(self) -> _lvgl.int32_t:
        return _lvgl.arc_get_max_value(self)

    def get_mode(self) -> _lvgl.arc_mode_t:
        return _lvgl.arc_get_mode(self)

    def get_rotation(self) -> _lvgl.int32_t:
        return _lvgl.arc_get_rotation(self)

    def get_knob_offset(self) -> _lvgl.int32_t:
        return _lvgl.arc_get_knob_offset(self)

    def get_change_rate(self) -> _lvgl.uint32_t:
        return _lvgl.arc_get_change_rate(self)

    def bind_value(self, subject: "subject_t") -> "observer_t":
        return _lvgl.arc_bind_value(self, subject)

    def align_obj_to_angle(self, obj_to_align: "obj", r_offset: _lvgl.int32_t) -> None:
        return _lvgl.arc_align_obj_to_angle(self, obj_to_align, r_offset)

    def rotate_obj_to_angle(self, obj_to_rotate: "obj", r_offset: _lvgl.int32_t) -> None:
        return _lvgl.arc_rotate_obj_to_angle(self, obj_to_rotate, r_offset)


class arclabel(obj):
    
    class DIR:
        CLOCKWISE = _lvgl.ARCLABEL_DIR_CLOCKWISE
        COUNTER_CLOCKWISE = _lvgl.ARCLABEL_DIR_COUNTER_CLOCKWISE
    
    class OVERFLOW:
        CLIP = _lvgl.ARCLABEL_OVERFLOW_CLIP
        ELLIPSIS = _lvgl.ARCLABEL_OVERFLOW_ELLIPSIS
        VISIBLE = _lvgl.ARCLABEL_OVERFLOW_VISIBLE
    
    class TEXT_ALIGN:
        CENTER = _lvgl.ARCLABEL_TEXT_ALIGN_CENTER
        DEFAULT = _lvgl.ARCLABEL_TEXT_ALIGN_DEFAULT
        LEADING = _lvgl.ARCLABEL_TEXT_ALIGN_LEADING
        TRAILING = _lvgl.ARCLABEL_TEXT_ALIGN_TRAILING

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.arclabel_create(parent)
            cls.cast(self)


    def set_text(self, text: _lvgl.char) -> None:
        return _lvgl.arclabel_set_text(self, text)

    def set_text_fmt(self, fmt: _lvgl.char, *args) -> None:
        return _lvgl.arclabel_set_text_fmt(self, fmt, *args)

    def set_text_static(self, text: _lvgl.char) -> None:
        return _lvgl.arclabel_set_text_static(self, text)

    def set_angle_start(self, start: _lvgl.value_precise_t) -> None:
        return _lvgl.arclabel_set_angle_start(self, start)

    def set_angle_size(self, size: _lvgl.value_precise_t) -> None:
        return _lvgl.arclabel_set_angle_size(self, size)

    def set_offset(self, offset: _lvgl.int32_t) -> None:
        return _lvgl.arclabel_set_offset(self, offset)

    def set_dir(self, dir: _lvgl.arclabel_dir_t) -> None:
        return _lvgl.arclabel_set_dir(self, dir)

    def set_recolor(self, en: _lvgl._Bool) -> None:
        return _lvgl.arclabel_set_recolor(self, en)

    def set_radius(self, radius: _lvgl.uint32_t) -> None:
        return _lvgl.arclabel_set_radius(self, radius)

    def set_center_offset_x(self, x: _lvgl.uint32_t) -> None:
        return _lvgl.arclabel_set_center_offset_x(self, x)

    def set_center_offset_y(self, y: _lvgl.uint32_t) -> None:
        return _lvgl.arclabel_set_center_offset_y(self, y)

    def set_text_vertical_align(self, align: _lvgl.arclabel_text_align_t) -> None:
        return _lvgl.arclabel_set_text_vertical_align(self, align)

    def set_text_horizontal_align(self, align: _lvgl.arclabel_text_align_t) -> None:
        return _lvgl.arclabel_set_text_horizontal_align(self, align)

    def set_overflow(self, overflow: _lvgl.arclabel_overflow_t) -> None:
        return _lvgl.arclabel_set_overflow(self, overflow)

    def set_end_overlap(self, overlap: _lvgl._Bool) -> None:
        return _lvgl.arclabel_set_end_overlap(self, overlap)

    def get_angle_start(self) -> _lvgl.value_precise_t:
        return _lvgl.arclabel_get_angle_start(self)

    def get_angle_size(self) -> _lvgl.value_precise_t:
        return _lvgl.arclabel_get_angle_size(self)

    def get_dir(self) -> _lvgl.arclabel_dir_t:
        return _lvgl.arclabel_get_dir(self)

    def get_recolor(self) -> _lvgl._Bool:
        return _lvgl.arclabel_get_recolor(self)

    def get_radius(self) -> _lvgl.uint32_t:
        return _lvgl.arclabel_get_radius(self)

    def get_center_offset_x(self) -> _lvgl.uint32_t:
        return _lvgl.arclabel_get_center_offset_x(self)

    def get_center_offset_y(self) -> _lvgl.uint32_t:
        return _lvgl.arclabel_get_center_offset_y(self)

    def get_text_vertical_align(self) -> _lvgl.arclabel_text_align_t:
        return _lvgl.arclabel_get_text_vertical_align(self)

    def get_text_horizontal_align(self) -> _lvgl.arclabel_text_align_t:
        return _lvgl.arclabel_get_text_horizontal_align(self)

    def get_overflow(self) -> _lvgl.arclabel_overflow_t:
        return _lvgl.arclabel_get_overflow(self)

    def get_end_overlap(self) -> _lvgl._Bool:
        return _lvgl.arclabel_get_end_overlap(self)

    def get_text_angle(self) -> _lvgl.value_precise_t:
        return _lvgl.arclabel_get_text_angle(self)


class label(obj):
    
    class LONG_MODE:
        CLIP = _lvgl.LABEL_LONG_MODE_CLIP
        DOTS = _lvgl.LABEL_LONG_MODE_DOTS
        SCROLL = _lvgl.LABEL_LONG_MODE_SCROLL
        SCROLL_CIRCULAR = _lvgl.LABEL_LONG_MODE_SCROLL_CIRCULAR
        WRAP = _lvgl.LABEL_LONG_MODE_WRAP

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.label_create(parent)
            cls.cast(self)


    def set_text(self, text: _lvgl.char) -> None:
        return _lvgl.label_set_text(self, text)

    def set_text_fmt(self, fmt: _lvgl.char, *args) -> None:
        return _lvgl.label_set_text_fmt(self, fmt, *args)

    def set_text_static(self, text: _lvgl.char) -> None:
        return _lvgl.label_set_text_static(self, text)

    def set_long_mode(self, long_mode: _lvgl.label_long_mode_t) -> None:
        return _lvgl.label_set_long_mode(self, long_mode)

    def set_text_selection_start(self, index: _lvgl.uint32_t) -> None:
        return _lvgl.label_set_text_selection_start(self, index)

    def set_text_selection_end(self, index: _lvgl.uint32_t) -> None:
        return _lvgl.label_set_text_selection_end(self, index)

    def set_recolor(self, en: _lvgl._Bool) -> None:
        return _lvgl.label_set_recolor(self, en)

    def get_text(self) -> _lvgl.char:
        return _lvgl.label_get_text(self)

    def get_long_mode(self) -> _lvgl.label_long_mode_t:
        return _lvgl.label_get_long_mode(self)

    def get_letter_pos(self, char_id: _lvgl.uint32_t, pos: _lvgl.point_t) -> None:
        return _lvgl.label_get_letter_pos(self, char_id, pos)

    def get_letter_on(self, pos_in: _lvgl.point_t, bidi: _lvgl._Bool) -> _lvgl.uint32_t:
        return _lvgl.label_get_letter_on(self, pos_in, bidi)

    def is_char_under_pos(self, pos: _lvgl.point_t) -> _lvgl._Bool:
        return _lvgl.label_is_char_under_pos(self, pos)

    def get_text_selection_start(self) -> _lvgl.uint32_t:
        return _lvgl.label_get_text_selection_start(self)

    def get_text_selection_end(self) -> _lvgl.uint32_t:
        return _lvgl.label_get_text_selection_end(self)

    def get_recolor(self) -> _lvgl._Bool:
        return _lvgl.label_get_recolor(self)

    def bind_text(self, subject: "subject_t", fmt: _lvgl.char) -> "observer_t":
        return _lvgl.label_bind_text(self, subject, fmt)

    def ins_text(self, pos: _lvgl.uint32_t, txt: _lvgl.char) -> None:
        return _lvgl.label_ins_text(self, pos, txt)

    def cut_text(self, pos: _lvgl.uint32_t, cnt: _lvgl.uint32_t) -> None:
        return _lvgl.label_cut_text(self, pos, cnt)


class bar(obj):
    
    class MODE:
        NORMAL = _lvgl.BAR_MODE_NORMAL
        RANGE = _lvgl.BAR_MODE_RANGE
        SYMMETRICAL = _lvgl.BAR_MODE_SYMMETRICAL
    
    class ORIENTATION:
        AUTO = _lvgl.BAR_ORIENTATION_AUTO
        HORIZONTAL = _lvgl.BAR_ORIENTATION_HORIZONTAL
        VERTICAL = _lvgl.BAR_ORIENTATION_VERTICAL

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.bar_create(parent)
            cls.cast(self)


    def set_value(self, value: _lvgl.int32_t, anim: _lvgl.anim_enable_t) -> None:
        return _lvgl.bar_set_value(self, value, anim)

    def set_start_value(self, start_value: _lvgl.int32_t, anim: _lvgl.anim_enable_t) -> None:
        return _lvgl.bar_set_start_value(self, start_value, anim)

    def set_range(self, min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.bar_set_range(self, min, max)

    def set_min_value(self, min: _lvgl.int32_t) -> None:
        return _lvgl.bar_set_min_value(self, min)

    def set_max_value(self, max: _lvgl.int32_t) -> None:
        return _lvgl.bar_set_max_value(self, max)

    def set_mode(self, mode: _lvgl.bar_mode_t) -> None:
        return _lvgl.bar_set_mode(self, mode)

    def set_orientation(self, orientation: _lvgl.bar_orientation_t) -> None:
        return _lvgl.bar_set_orientation(self, orientation)

    def get_value(self) -> _lvgl.int32_t:
        return _lvgl.bar_get_value(self)

    def get_start_value(self) -> _lvgl.int32_t:
        return _lvgl.bar_get_start_value(self)

    def get_min_value(self) -> _lvgl.int32_t:
        return _lvgl.bar_get_min_value(self)

    def get_max_value(self) -> _lvgl.int32_t:
        return _lvgl.bar_get_max_value(self)

    def get_mode(self) -> _lvgl.bar_mode_t:
        return _lvgl.bar_get_mode(self)

    def get_orientation(self) -> _lvgl.bar_orientation_t:
        return _lvgl.bar_get_orientation(self)

    def is_symmetrical(self) -> _lvgl._Bool:
        return _lvgl.bar_is_symmetrical(self)

    def bind_value(self, subject: "subject_t") -> "observer_t":
        return _lvgl.bar_bind_value(self, subject)


class button(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.button_create(parent)
            cls.cast(self)




class buttonmatrix(obj):
    
    class CTRL:
        CHECKABLE = _lvgl.BUTTONMATRIX_CTRL_CHECKABLE
        CHECKED = _lvgl.BUTTONMATRIX_CTRL_CHECKED
        CLICK_TRIG = _lvgl.BUTTONMATRIX_CTRL_CLICK_TRIG
        CUSTOM_1 = _lvgl.BUTTONMATRIX_CTRL_CUSTOM_1
        CUSTOM_2 = _lvgl.BUTTONMATRIX_CTRL_CUSTOM_2
        DISABLED = _lvgl.BUTTONMATRIX_CTRL_DISABLED
        HIDDEN = _lvgl.BUTTONMATRIX_CTRL_HIDDEN
        NONE = _lvgl.BUTTONMATRIX_CTRL_NONE
        NO_REPEAT = _lvgl.BUTTONMATRIX_CTRL_NO_REPEAT
        POPOVER = _lvgl.BUTTONMATRIX_CTRL_POPOVER
        RECOLOR = _lvgl.BUTTONMATRIX_CTRL_RECOLOR
        RESERVED_1 = _lvgl.BUTTONMATRIX_CTRL_RESERVED_1
        RESERVED_2 = _lvgl.BUTTONMATRIX_CTRL_RESERVED_2
        WIDTH_1 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_1
        WIDTH_10 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_10
        WIDTH_11 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_11
        WIDTH_12 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_12
        WIDTH_13 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_13
        WIDTH_14 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_14
        WIDTH_15 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_15
        WIDTH_2 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_2
        WIDTH_3 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_3
        WIDTH_4 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_4
        WIDTH_5 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_5
        WIDTH_6 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_6
        WIDTH_7 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_7
        WIDTH_8 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_8
        WIDTH_9 = _lvgl.BUTTONMATRIX_CTRL_WIDTH_9

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.buttonmatrix_create(parent)
            cls.cast(self)


    def set_map(self, map: "List") -> None:
        return _lvgl.buttonmatrix_set_map(self, map)

    def set_ctrl_map(self, ctrl_map: "List") -> None:
        return _lvgl.buttonmatrix_set_ctrl_map(self, ctrl_map)

    def set_selected_button(self, btn_id: _lvgl.uint32_t) -> None:
        return _lvgl.buttonmatrix_set_selected_button(self, btn_id)

    def set_button_ctrl(self, btn_id: _lvgl.uint32_t, ctrl: _lvgl.buttonmatrix_ctrl_t) -> None:
        return _lvgl.buttonmatrix_set_button_ctrl(self, btn_id, ctrl)

    def clear_button_ctrl(self, btn_id: _lvgl.uint32_t, ctrl: _lvgl.buttonmatrix_ctrl_t) -> None:
        return _lvgl.buttonmatrix_clear_button_ctrl(self, btn_id, ctrl)

    def set_button_ctrl_all(self, ctrl: _lvgl.buttonmatrix_ctrl_t) -> None:
        return _lvgl.buttonmatrix_set_button_ctrl_all(self, ctrl)

    def clear_button_ctrl_all(self, ctrl: _lvgl.buttonmatrix_ctrl_t) -> None:
        return _lvgl.buttonmatrix_clear_button_ctrl_all(self, ctrl)

    def set_button_width(self, btn_id: _lvgl.uint32_t, width: _lvgl.uint32_t) -> None:
        return _lvgl.buttonmatrix_set_button_width(self, btn_id, width)

    def set_one_checked(self, en: _lvgl._Bool) -> None:
        return _lvgl.buttonmatrix_set_one_checked(self, en)

    def get_map(self) -> _lvgl.char:
        return _lvgl.buttonmatrix_get_map(self)

    def get_selected_button(self) -> _lvgl.uint32_t:
        return _lvgl.buttonmatrix_get_selected_button(self)

    def get_button_text(self, btn_id: _lvgl.uint32_t) -> _lvgl.char:
        return _lvgl.buttonmatrix_get_button_text(self, btn_id)

    def has_button_ctrl(self, btn_id: _lvgl.uint32_t, ctrl: _lvgl.buttonmatrix_ctrl_t) -> _lvgl._Bool:
        return _lvgl.buttonmatrix_has_button_ctrl(self, btn_id, ctrl)

    def get_one_checked(self) -> _lvgl._Bool:
        return _lvgl.buttonmatrix_get_one_checked(self)


class calendar(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.calendar_create(parent)
            cls.cast(self)


    def set_today_date(self, year: _lvgl.uint32_t, month: _lvgl.uint32_t, day: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_today_date(self, year, month, day)

    def set_today_year(self, year: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_today_year(self, year)

    def set_today_month(self, month: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_today_month(self, month)

    def set_today_day(self, day: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_today_day(self, day)

    def set_month_shown(self, year: _lvgl.uint32_t, month: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_month_shown(self, year, month)

    def set_shown_year(self, year: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_shown_year(self, year)

    def set_shown_month(self, month: _lvgl.uint32_t) -> None:
        return _lvgl.calendar_set_shown_month(self, month)

    def set_highlighted_dates(self, highlighted: "List", date_num: _lvgl.size_t) -> None:
        return _lvgl.calendar_set_highlighted_dates(self, highlighted, date_num)

    def set_day_names(self, day_names: _lvgl.char) -> None:
        return _lvgl.calendar_set_day_names(self, day_names)

    def get_btnmatrix(self) -> "obj":
        return _wrap_obj(_lvgl.calendar_get_btnmatrix(self))

    def get_today_date(self) -> "calendar_date_t":
        return _lvgl.calendar_get_today_date(self)

    def get_showed_date(self) -> "calendar_date_t":
        return _lvgl.calendar_get_showed_date(self)

    def get_highlighted_dates(self) -> "calendar_date_t":
        return _lvgl.calendar_get_highlighted_dates(self)

    def get_highlighted_dates_num(self) -> _lvgl.size_t:
        return _lvgl.calendar_get_highlighted_dates_num(self)

    def get_pressed_date(self, date: "calendar_date_t") -> _lvgl.result_t:
        return _lvgl.calendar_get_pressed_date(self, date)

    def add_header_arrow(self) -> "obj":
        return _wrap_obj(_lvgl.calendar_add_header_arrow(self))

    def add_header_dropdown(self) -> "obj":
        return _wrap_obj(_lvgl.calendar_add_header_dropdown(self))

    def header_dropdown_set_year_list(self, years_list: _lvgl.char) -> None:
        return _lvgl.calendar_header_dropdown_set_year_list(self, years_list)


class canvas(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.canvas_create(parent)
            cls.cast(self)


    def set_buffer(self, buf: None, w: _lvgl.int32_t, h: _lvgl.int32_t, cf: _lvgl.color_format_t) -> None:
        _retain_obj_ref(self, 'canvas_buffer', buf)
        return _lvgl.canvas_set_buffer(self, buf, w, h, cf)

    def set_draw_buf(self, draw_buf: "draw_buf_t") -> None:
        return _lvgl.canvas_set_draw_buf(self, draw_buf)

    def set_px(self, x: _lvgl.int32_t, y: _lvgl.int32_t, color: "color_t", opa: _lvgl.opa_t) -> None:
        return _lvgl.canvas_set_px(self, x, y, color, opa)

    def set_palette(self, index: _lvgl.uint8_t, color: "color32_t") -> None:
        return _lvgl.canvas_set_palette(self, index, color)

    def get_draw_buf(self) -> "draw_buf_t":
        return _lvgl.canvas_get_draw_buf(self)

    def get_px(self, x: _lvgl.int32_t, y: _lvgl.int32_t) -> "color32_t":
        return _lvgl.canvas_get_px(self, x, y)

    def get_image(self) -> "image_dsc_t":
        return _lvgl.canvas_get_image(self)

    def get_buf(self) -> "Any":
        return _lvgl.canvas_get_buf(self)

    def copy_buf(self, canvas_area: "area_t", src_buf: "draw_buf_t", src_area: "area_t") -> None:
        return _lvgl.canvas_copy_buf(self, canvas_area, src_buf, src_area)

    def fill_bg(self, color: "color_t", opa: _lvgl.opa_t) -> None:
        return _lvgl.canvas_fill_bg(self, color, opa)

    def init_layer(self, layer: "layer_t") -> None:
        return _lvgl.canvas_init_layer(self, layer)

    def finish_layer(self, layer: "layer_t") -> None:
        return _lvgl.canvas_finish_layer(self, layer)


class chart(obj):
    
    class AXIS_PRIMARY:
        X = _lvgl.CHART_AXIS_PRIMARY_X
        Y = _lvgl.CHART_AXIS_PRIMARY_Y
    
    class AXIS_SECONDARY:
        X = _lvgl.CHART_AXIS_SECONDARY_X
        Y = _lvgl.CHART_AXIS_SECONDARY_Y
    
    class TYPE:
        BAR = _lvgl.CHART_TYPE_BAR
        CURVE = _lvgl.CHART_TYPE_CURVE
        LINE = _lvgl.CHART_TYPE_LINE
        NONE = _lvgl.CHART_TYPE_NONE
        SCATTER = _lvgl.CHART_TYPE_SCATTER
        STACKED = _lvgl.CHART_TYPE_STACKED
    
    class UPDATE_MODE:
        CIRCULAR = _lvgl.CHART_UPDATE_MODE_CIRCULAR
        SHIFT = _lvgl.CHART_UPDATE_MODE_SHIFT

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.chart_create(parent)
            cls.cast(self)


    def set_type(self, type: _lvgl.chart_type_t) -> None:
        return _lvgl.chart_set_type(self, type)

    def set_point_count(self, cnt: _lvgl.uint32_t) -> None:
        return _lvgl.chart_set_point_count(self, cnt)

    def set_axis_range(self, axis: _lvgl.chart_axis_t, min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_axis_range(self, axis, min, max)

    def set_axis_min_value(self, axis: _lvgl.chart_axis_t, min: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_axis_min_value(self, axis, min)

    def set_axis_max_value(self, axis: _lvgl.chart_axis_t, max: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_axis_max_value(self, axis, max)

    def set_update_mode(self, update_mode: _lvgl.chart_update_mode_t) -> None:
        return _lvgl.chart_set_update_mode(self, update_mode)

    def set_div_line_count(self, hdiv: _lvgl.uint32_t, vdiv: _lvgl.uint32_t) -> None:
        return _lvgl.chart_set_div_line_count(self, hdiv, vdiv)

    def set_hor_div_line_count(self, cnt: _lvgl.uint32_t) -> None:
        return _lvgl.chart_set_hor_div_line_count(self, cnt)

    def set_ver_div_line_count(self, cnt: _lvgl.uint32_t) -> None:
        return _lvgl.chart_set_ver_div_line_count(self, cnt)

    def get_type(self) -> _lvgl.chart_type_t:
        return _lvgl.chart_get_type(self)

    def get_point_count(self) -> _lvgl.uint32_t:
        return _lvgl.chart_get_point_count(self)

    def get_update_mode(self) -> _lvgl.chart_update_mode_t:
        return _lvgl.chart_get_update_mode(self)

    def get_hor_div_line_count(self) -> _lvgl.uint32_t:
        return _lvgl.chart_get_hor_div_line_count(self)

    def get_ver_div_line_count(self) -> _lvgl.uint32_t:
        return _lvgl.chart_get_ver_div_line_count(self)

    def get_x_start_point(self, ser: _lvgl.chart_series_t) -> _lvgl.uint32_t:
        return _lvgl.chart_get_x_start_point(self, ser)

    def get_point_pos_by_id(self, ser: _lvgl.chart_series_t, id: _lvgl.uint32_t, p_out: _lvgl.point_t) -> None:
        return _lvgl.chart_get_point_pos_by_id(self, ser, id, p_out)

    def refresh(self) -> None:
        return _lvgl.chart_refresh(self)

    def add_series(self, color: "color_t", axis: _lvgl.chart_axis_t) -> _lvgl.chart_series_t:
        return _lvgl.chart_add_series(self, color, axis)

    def remove_series(self, series: _lvgl.chart_series_t) -> None:
        return _lvgl.chart_remove_series(self, series)

    def hide_series(self, series: _lvgl.chart_series_t, hide: _lvgl._Bool) -> None:
        return _lvgl.chart_hide_series(self, series, hide)

    def set_series_color(self, series: _lvgl.chart_series_t, color: "color_t") -> None:
        return _lvgl.chart_set_series_color(self, series, color)

    def get_series_color(self, series: _lvgl.chart_series_t) -> "color_t":
        return _lvgl.chart_get_series_color(self, series)

    def set_x_start_point(self, ser: _lvgl.chart_series_t, id: _lvgl.uint32_t) -> None:
        return _lvgl.chart_set_x_start_point(self, ser, id)

    def get_series_next(self, ser: _lvgl.chart_series_t) -> _lvgl.chart_series_t:
        return _lvgl.chart_get_series_next(self, ser)

    def add_cursor(self, color: "color_t", dir: _lvgl.dir_t) -> _lvgl.chart_cursor_t:
        return _lvgl.chart_add_cursor(self, color, dir)

    def remove_cursor(self, cursor: _lvgl.chart_cursor_t) -> None:
        return _lvgl.chart_remove_cursor(self, cursor)

    def set_cursor_pos(self, cursor: _lvgl.chart_cursor_t, pos: _lvgl.point_t) -> None:
        return _lvgl.chart_set_cursor_pos(self, cursor, pos)

    def set_cursor_pos_x(self, cursor: _lvgl.chart_cursor_t, x: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_cursor_pos_x(self, cursor, x)

    def set_cursor_pos_y(self, cursor: _lvgl.chart_cursor_t, y: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_cursor_pos_y(self, cursor, y)

    def set_cursor_point(self, cursor: _lvgl.chart_cursor_t, ser: _lvgl.chart_series_t, point_id: _lvgl.uint32_t) -> None:
        return _lvgl.chart_set_cursor_point(self, cursor, ser, point_id)

    def get_cursor_point(self, cursor: _lvgl.chart_cursor_t) -> _lvgl.point_t:
        return _lvgl.chart_get_cursor_point(self, cursor)

    def set_all_values(self, ser: _lvgl.chart_series_t, value: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_all_values(self, ser, value)

    def set_next_value(self, ser: _lvgl.chart_series_t, value: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_next_value(self, ser, value)

    def set_next_value2(self, ser: _lvgl.chart_series_t, x_value: _lvgl.int32_t, y_value: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_next_value2(self, ser, x_value, y_value)

    def set_series_values(self, ser: _lvgl.chart_series_t, values: "List", values_cnt: _lvgl.size_t) -> None:
        return _lvgl.chart_set_series_values(self, ser, values, values_cnt)

    def set_series_values2(self, ser: _lvgl.chart_series_t, x_values: "List", y_values: "List", values_cnt: _lvgl.size_t) -> None:
        return _lvgl.chart_set_series_values2(self, ser, x_values, y_values, values_cnt)

    def set_series_value_by_id(self, ser: _lvgl.chart_series_t, id: _lvgl.uint32_t, value: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_series_value_by_id(self, ser, id, value)

    def set_series_value_by_id2(self, ser: _lvgl.chart_series_t, id: _lvgl.uint32_t, x_value: _lvgl.int32_t, y_value: _lvgl.int32_t) -> None:
        return _lvgl.chart_set_series_value_by_id2(self, ser, id, x_value, y_value)

    def set_series_ext_y_array(self, ser: _lvgl.chart_series_t, array: "List") -> None:
        return _lvgl.chart_set_series_ext_y_array(self, ser, array)

    def set_series_ext_x_array(self, ser: _lvgl.chart_series_t, array: "List") -> None:
        return _lvgl.chart_set_series_ext_x_array(self, ser, array)

    def get_series_y_array(self, ser: _lvgl.chart_series_t) -> _lvgl.int32_t:
        return _lvgl.chart_get_series_y_array(self, ser)

    def get_series_x_array(self, ser: _lvgl.chart_series_t) -> _lvgl.int32_t:
        return _lvgl.chart_get_series_x_array(self, ser)

    def get_pressed_point(self) -> _lvgl.uint32_t:
        return _lvgl.chart_get_pressed_point(self)

    def get_first_point_center_offset(self) -> _lvgl.int32_t:
        return _lvgl.chart_get_first_point_center_offset(self)


class checkbox(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.checkbox_create(parent)
            cls.cast(self)


    def set_text(self, txt: _lvgl.char) -> None:
        return _lvgl.checkbox_set_text(self, txt)

    def set_text_static(self, txt: _lvgl.char) -> None:
        return _lvgl.checkbox_set_text_static(self, txt)

    def get_text(self) -> _lvgl.char:
        return _lvgl.checkbox_get_text(self)


class dropdown(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.dropdown_create(parent)
            cls.cast(self)


    def set_text(self, text: _lvgl.char) -> None:
        return _lvgl.dropdown_set_text(self, text)

    def set_text_static(self, text: _lvgl.char) -> None:
        return _lvgl.dropdown_set_text_static(self, text)

    def set_options(self, options: _lvgl.char) -> None:
        return _lvgl.dropdown_set_options(self, options)

    def set_options_static(self, options: _lvgl.char) -> None:
        return _lvgl.dropdown_set_options_static(self, options)

    def add_option(self, option: _lvgl.char, pos: _lvgl.uint32_t) -> None:
        return _lvgl.dropdown_add_option(self, option, pos)

    def clear_options(self) -> None:
        return _lvgl.dropdown_clear_options(self)

    def set_selected(self, sel_opt: _lvgl.uint32_t) -> None:
        return _lvgl.dropdown_set_selected(self, sel_opt)

    def set_dir(self, dir: _lvgl.dir_t) -> None:
        return _lvgl.dropdown_set_dir(self, dir)

    def set_symbol(self, symbol: None) -> None:
        return _lvgl.dropdown_set_symbol(self, symbol)

    def set_selected_highlight(self, en: _lvgl._Bool) -> None:
        return _lvgl.dropdown_set_selected_highlight(self, en)

    def get_list(self) -> "obj":
        return _wrap_obj(_lvgl.dropdown_get_list(self))

    def get_text(self) -> _lvgl.char:
        return _lvgl.dropdown_get_text(self)

    def get_options(self) -> _lvgl.char:
        return _lvgl.dropdown_get_options(self)

    def get_selected(self) -> _lvgl.uint32_t:
        return _lvgl.dropdown_get_selected(self)

    def get_option_count(self) -> _lvgl.uint32_t:
        return _lvgl.dropdown_get_option_count(self)

    def get_selected_str(self, buf: _lvgl.char, buf_size: _lvgl.uint32_t) -> None:
        return _lvgl.dropdown_get_selected_str(self, buf, buf_size)

    def get_option_index(self, option: _lvgl.char) -> _lvgl.int32_t:
        return _lvgl.dropdown_get_option_index(self, option)

    def get_symbol(self) -> _lvgl.char:
        return _lvgl.dropdown_get_symbol(self)

    def get_selected_highlight(self) -> _lvgl._Bool:
        return _lvgl.dropdown_get_selected_highlight(self)

    def get_dir(self) -> _lvgl.dir_t:
        return _lvgl.dropdown_get_dir(self)

    def open(self) -> None:
        return _lvgl.dropdown_open(self)

    def close(self) -> None:
        return _lvgl.dropdown_close(self)

    def is_open(self) -> _lvgl._Bool:
        return _lvgl.dropdown_is_open(self)

    def bind_value(self, subject: "subject_t") -> "observer_t":
        return _lvgl.dropdown_bind_value(self, subject)


class gif(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.gif_create(parent)
            cls.cast(self)


    def set_color_format(self, color_format: _lvgl.color_format_t) -> None:
        return _lvgl.gif_set_color_format(self, color_format)

    def set_src(self, src: None) -> None:
        return _lvgl.gif_set_src(self, src)

    def restart(self) -> None:
        return _lvgl.gif_restart(self)

    def pause(self) -> None:
        return _lvgl.gif_pause(self)

    def resume(self) -> None:
        return _lvgl.gif_resume(self)

    def is_loaded(self) -> _lvgl._Bool:
        return _lvgl.gif_is_loaded(self)

    def get_loop_count(self) -> _lvgl.int32_t:
        return _lvgl.gif_get_loop_count(self)

    def set_loop_count(self, count: _lvgl.int32_t) -> None:
        return _lvgl.gif_set_loop_count(self, count)

    def set_auto_pause_invisible(self, auto_pause: _lvgl._Bool) -> None:
        return _lvgl.gif_set_auto_pause_invisible(self, auto_pause)

    def get_frame_count(self) -> _lvgl.int32_t:
        return _lvgl.gif_get_frame_count(self)

    def get_current_frame_index(self) -> _lvgl.int32_t:
        return _lvgl.gif_get_current_frame_index(self)


class imagebutton(obj):
    
    class STATE_CHECKED:
        DISABLED = _lvgl.IMAGEBUTTON_STATE_DISABLED
        PRESSED = _lvgl.IMAGEBUTTON_STATE_PRESSED
        RELEASED = _lvgl.IMAGEBUTTON_STATE_RELEASED
        NUM = _lvgl.IMAGEBUTTON_STATE_NUM

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.imagebutton_create(parent)
            cls.cast(self)


    def set_src(self, state: _lvgl.imagebutton_state_t, src_left: None, src_mid: None, src_right: None) -> None:
        return _lvgl.imagebutton_set_src(self, state, src_left, src_mid, src_right)

    def set_src_left(self, state: _lvgl.imagebutton_state_t, src_left: None) -> None:
        return _lvgl.imagebutton_set_src_left(self, state, src_left)

    def set_src_right(self, state: _lvgl.imagebutton_state_t, src_right: None) -> None:
        return _lvgl.imagebutton_set_src_right(self, state, src_right)

    def set_src_mid(self, state: _lvgl.imagebutton_state_t, src_mid: None) -> None:
        return _lvgl.imagebutton_set_src_mid(self, state, src_mid)

    def set_state(self, state: _lvgl.imagebutton_state_t) -> None:
        return _lvgl.imagebutton_set_state(self, state)

    def get_src_left(self, state: _lvgl.imagebutton_state_t) -> "Any":
        return _lvgl.imagebutton_get_src_left(self, state)

    def get_src_middle(self, state: _lvgl.imagebutton_state_t) -> "Any":
        return _lvgl.imagebutton_get_src_middle(self, state)

    def get_src_right(self, state: _lvgl.imagebutton_state_t) -> "Any":
        return _lvgl.imagebutton_get_src_right(self, state)


class keyboard(obj):
    
    class MODE:
        NUMBER = _lvgl.KEYBOARD_MODE_NUMBER
        SPECIAL = _lvgl.KEYBOARD_MODE_SPECIAL
        TEXT_LOWER = _lvgl.KEYBOARD_MODE_TEXT_LOWER
        TEXT_UPPER = _lvgl.KEYBOARD_MODE_TEXT_UPPER
        USER_1 = _lvgl.KEYBOARD_MODE_USER_1
        USER_2 = _lvgl.KEYBOARD_MODE_USER_2
        USER_3 = _lvgl.KEYBOARD_MODE_USER_3
        USER_4 = _lvgl.KEYBOARD_MODE_USER_4

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.keyboard_create(parent)
            cls.cast(self)


    def set_textarea(self, ta: "obj") -> None:
        return _lvgl.keyboard_set_textarea(self, ta)

    def set_mode(self, mode: _lvgl.keyboard_mode_t) -> None:
        return _lvgl.keyboard_set_mode(self, mode)

    def set_popovers(self, en: _lvgl._Bool) -> None:
        return _lvgl.keyboard_set_popovers(self, en)

    def set_map(self, mode: _lvgl.keyboard_mode_t, map: "List", ctrl_map: "List") -> None:
        return _lvgl.keyboard_set_map(self, mode, map, ctrl_map)

    def get_textarea(self) -> "obj":
        return _wrap_obj(_lvgl.keyboard_get_textarea(self))

    def get_mode(self) -> _lvgl.keyboard_mode_t:
        return _lvgl.keyboard_get_mode(self)

    def get_popovers(self) -> _lvgl._Bool:
        return _lvgl.keyboard_get_popovers(self)

    def get_map_array(self) -> _lvgl.char:
        return _lvgl.keyboard_get_map_array(self)

    def get_selected_button(self) -> _lvgl.uint32_t:
        return _lvgl.keyboard_get_selected_button(self)

    def get_button_text(self, btn_id: _lvgl.uint32_t) -> _lvgl.char:
        return _lvgl.keyboard_get_button_text(self, btn_id)


class led(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.led_create(parent)
            cls.cast(self)


    def set_color(self, color: "color_t") -> None:
        return _lvgl.led_set_color(self, color)

    def set_brightness(self, bright: _lvgl.uint8_t) -> None:
        return _lvgl.led_set_brightness(self, bright)

    def on(self) -> None:
        return _lvgl.led_on(self)

    def off(self) -> None:
        return _lvgl.led_off(self)

    def toggle(self) -> None:
        return _lvgl.led_toggle(self)

    def get_brightness(self) -> _lvgl.uint8_t:
        return _lvgl.led_get_brightness(self)

    def get_color(self) -> "color_t":
        return _lvgl.led_get_color(self)


class line(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.line_create(parent)
            cls.cast(self)


    def set_points(self, points: "List", point_num: _lvgl.uint32_t) -> None:
        return _lvgl.line_set_points(self, points, point_num)

    def set_points_mutable(self, points: "List", point_num: _lvgl.uint32_t) -> None:
        return _lvgl.line_set_points_mutable(self, points, point_num)

    def set_y_invert(self, en: _lvgl._Bool) -> None:
        return _lvgl.line_set_y_invert(self, en)

    def get_points(self) -> _lvgl.point_precise_t:
        return _lvgl.line_get_points(self)

    def get_point_count(self) -> _lvgl.uint32_t:
        return _lvgl.line_get_point_count(self)

    def is_point_array_mutable(self) -> _lvgl._Bool:
        return _lvgl.line_is_point_array_mutable(self)

    def get_points_mutable(self) -> _lvgl.point_precise_t:
        return _lvgl.line_get_points_mutable(self)

    def get_y_invert(self) -> _lvgl._Bool:
        return _lvgl.line_get_y_invert(self)


class list(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.list_create(parent)
            cls.cast(self)


    def add_text(self, txt: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.list_add_text(self, txt))

    def add_button(self, icon: None, txt: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.list_add_button(self, icon, txt))

    def get_button_text(self, btn: "obj") -> _lvgl.char:
        return _lvgl.list_get_button_text(self, btn)

    def set_button_text(self, btn: "obj", txt: _lvgl.char) -> None:
        return _lvgl.list_set_button_text(self, btn, txt)


class menu(obj):
    
    class HEADER:
        BOTTOM_FIXED = _lvgl.MENU_HEADER_BOTTOM_FIXED
        TOP_FIXED = _lvgl.MENU_HEADER_TOP_FIXED
        TOP_UNFIXED = _lvgl.MENU_HEADER_TOP_UNFIXED
    
    class ROOT_BACK:
        BUTTON_DISABLED = _lvgl.MENU_ROOT_BACK_BUTTON_DISABLED
        BUTTON_ENABLED = _lvgl.MENU_ROOT_BACK_BUTTON_ENABLED

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.menu_create(parent)
            cls.cast(self)


    def set_page(self, page: "obj") -> None:
        return _lvgl.menu_set_page(self, page)

    def set_page_title(self, title: _lvgl.char) -> None:
        return _lvgl.menu_set_page_title(self, title)

    def set_page_title_static(self, title: _lvgl.char) -> None:
        return _lvgl.menu_set_page_title_static(self, title)

    def set_sidebar_page(self, page: "obj") -> None:
        return _lvgl.menu_set_sidebar_page(self, page)

    def set_mode_header(self, mode: _lvgl.menu_mode_header_t) -> None:
        return _lvgl.menu_set_mode_header(self, mode)

    def set_mode_root_back_button(self, mode: _lvgl.menu_mode_root_back_button_t) -> None:
        return _lvgl.menu_set_mode_root_back_button(self, mode)

    def set_load_page_event(self, obj: "obj", page: "obj") -> None:
        return _lvgl.menu_set_load_page_event(self, obj, page)

    def get_cur_main_page(self) -> "obj":
        return _wrap_obj(_lvgl.menu_get_cur_main_page(self))

    def get_cur_sidebar_page(self) -> "obj":
        return _wrap_obj(_lvgl.menu_get_cur_sidebar_page(self))

    def get_main_header(self) -> "obj":
        return _wrap_obj(_lvgl.menu_get_main_header(self))

    def get_main_header_back_button(self) -> "obj":
        return _wrap_obj(_lvgl.menu_get_main_header_back_button(self))

    def get_sidebar_header(self) -> "obj":
        return _wrap_obj(_lvgl.menu_get_sidebar_header(self))

    def get_sidebar_header_back_button(self) -> "obj":
        return _wrap_obj(_lvgl.menu_get_sidebar_header_back_button(self))

    def back_button_is_root(self, obj: "obj") -> _lvgl._Bool:
        return _lvgl.menu_back_button_is_root(self, obj)

    def get_mode_header(self) -> _lvgl.menu_mode_header_t:
        return _lvgl.menu_get_mode_header(self)

    def get_mode_root_back_button(self) -> _lvgl.menu_mode_root_back_button_t:
        return _lvgl.menu_get_mode_root_back_button(self)

    def clear_history(self) -> None:
        return _lvgl.menu_clear_history(self)


class menu_page(obj):

    def __init__(self, menu: _lvgl.obj_t, title: _lvgl.char):
        for arg in (menu, title,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.menu_page_create(menu, title)
            cls.cast(self)




class menu_cont(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.menu_cont_create(parent)
            cls.cast(self)




class menu_section(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.menu_section_create(parent)
            cls.cast(self)




class menu_separator(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.menu_separator_create(parent)
            cls.cast(self)




class msgbox(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.msgbox_create(parent)
            cls.cast(self)


    def add_title(self, title: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.msgbox_add_title(self, title))

    def add_header_button(self, icon: None) -> "obj":
        return _wrap_obj(_lvgl.msgbox_add_header_button(self, icon))

    def add_text(self, text: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.msgbox_add_text(self, text))

    def add_text_fmt(self, fmt: _lvgl.char, *args) -> "obj":
        return _wrap_obj(_lvgl.msgbox_add_text_fmt(self, fmt, *args))

    def add_footer_button(self, text: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.msgbox_add_footer_button(self, text))

    def add_close_button(self) -> "obj":
        return _wrap_obj(_lvgl.msgbox_add_close_button(self))

    def get_header(self) -> "obj":
        return _wrap_obj(_lvgl.msgbox_get_header(self))

    def get_footer(self) -> "obj":
        return _wrap_obj(_lvgl.msgbox_get_footer(self))

    def get_content(self) -> "obj":
        return _wrap_obj(_lvgl.msgbox_get_content(self))

    def get_title(self) -> "obj":
        return _wrap_obj(_lvgl.msgbox_get_title(self))

    def close(self) -> None:
        return _lvgl.msgbox_close(self)

    def close_async(self) -> None:
        return _lvgl.msgbox_close_async(self)


class roller(obj):
    
    class MODE:
        INFINITE = _lvgl.ROLLER_MODE_INFINITE
        NORMAL = _lvgl.ROLLER_MODE_NORMAL

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.roller_create(parent)
            cls.cast(self)


    def set_options(self, options: _lvgl.char, mode: _lvgl.roller_mode_t) -> None:
        return _lvgl.roller_set_options(self, options, mode)

    def set_selected(self, sel_opt: _lvgl.uint32_t, anim: _lvgl.anim_enable_t) -> None:
        return _lvgl.roller_set_selected(self, sel_opt, anim)

    def set_selected_str(self, sel_opt: _lvgl.char, anim: _lvgl.anim_enable_t) -> _lvgl._Bool:
        return _lvgl.roller_set_selected_str(self, sel_opt, anim)

    def set_visible_row_count(self, row_cnt: _lvgl.uint32_t) -> None:
        return _lvgl.roller_set_visible_row_count(self, row_cnt)

    def get_selected(self) -> _lvgl.uint32_t:
        return _lvgl.roller_get_selected(self)

    def get_selected_str(self, buf: _lvgl.char, buf_size: _lvgl.uint32_t) -> None:
        return _lvgl.roller_get_selected_str(self, buf, buf_size)

    def get_options(self) -> _lvgl.char:
        return _lvgl.roller_get_options(self)

    def get_option_count(self) -> _lvgl.uint32_t:
        return _lvgl.roller_get_option_count(self)

    def get_option_str(self, option: _lvgl.uint32_t, buf: _lvgl.char, buf_size: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.roller_get_option_str(self, option, buf, buf_size)

    def bind_value(self, subject: "subject_t") -> "observer_t":
        return _lvgl.roller_bind_value(self, subject)


class scale(obj):
    
    class LABEL:
        ENABLED_DEFAULT = _lvgl.SCALE_LABEL_ENABLED_DEFAULT
        ROTATE_KEEP_UPRIGHT = _lvgl.SCALE_LABEL_ROTATE_KEEP_UPRIGHT
        ROTATE_MATCH_TICKS = _lvgl.SCALE_LABEL_ROTATE_MATCH_TICKS
    
    class MODE_HORIZONTAL:
        BOTTOM = _lvgl.SCALE_MODE_HORIZONTAL_BOTTOM
        TOP = _lvgl.SCALE_MODE_HORIZONTAL_TOP
        LAST = _lvgl.SCALE_MODE_LAST
        ROUND_INNER = _lvgl.SCALE_MODE_ROUND_INNER
        ROUND_OUTER = _lvgl.SCALE_MODE_ROUND_OUTER
        VERTICAL_LEFT = _lvgl.SCALE_MODE_VERTICAL_LEFT
        VERTICAL_RIGHT = _lvgl.SCALE_MODE_VERTICAL_RIGHT

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.scale_create(parent)
            cls.cast(self)


    def set_mode(self, mode: _lvgl.scale_mode_t) -> None:
        return _lvgl.scale_set_mode(self, mode)

    def set_total_tick_count(self, total_tick_count: _lvgl.uint32_t) -> None:
        return _lvgl.scale_set_total_tick_count(self, total_tick_count)

    def set_major_tick_every(self, major_tick_every: _lvgl.uint32_t) -> None:
        return _lvgl.scale_set_major_tick_every(self, major_tick_every)

    def set_label_show(self, show_label: _lvgl._Bool) -> None:
        return _lvgl.scale_set_label_show(self, show_label)

    def set_range(self, min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_range(self, min, max)

    def set_min_value(self, min: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_min_value(self, min)

    def set_max_value(self, max: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_max_value(self, max)

    def set_angle_range(self, angle_range: _lvgl.uint32_t) -> None:
        return _lvgl.scale_set_angle_range(self, angle_range)

    def set_rotation(self, rotation: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_rotation(self, rotation)

    def set_line_needle_value(self, needle_line: "obj", needle_length: _lvgl.int32_t, value: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_line_needle_value(self, needle_line, needle_length, value)

    def set_image_needle_value(self, needle_img: "obj", value: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_image_needle_value(self, needle_img, value)

    def set_text_src(self, txt_src: "List") -> None:
        return _lvgl.scale_set_text_src(self, txt_src)

    def set_post_draw(self, en: _lvgl._Bool) -> None:
        return _lvgl.scale_set_post_draw(self, en)

    def set_draw_ticks_on_top(self, en: _lvgl._Bool) -> None:
        return _lvgl.scale_set_draw_ticks_on_top(self, en)

    def add_section(self) -> "scale_section_t":
        return _lvgl.scale_add_section(self)

    def set_section_range(self, section: "scale_section_t", min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_section_range(self, section, min, max)

    def set_section_min_value(self, section: "scale_section_t", min: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_section_min_value(self, section, min)

    def set_section_max_value(self, section: "scale_section_t", max: _lvgl.int32_t) -> None:
        return _lvgl.scale_set_section_max_value(self, section, max)

    def set_section_style_main(self, section: "scale_section_t", style: "style_t") -> None:
        return _lvgl.scale_set_section_style_main(self, section, style)

    def set_section_style_indicator(self, section: "scale_section_t", style: "style_t") -> None:
        return _lvgl.scale_set_section_style_indicator(self, section, style)

    def set_section_style_items(self, section: "scale_section_t", style: "style_t") -> None:
        return _lvgl.scale_set_section_style_items(self, section, style)

    def get_mode(self) -> _lvgl.scale_mode_t:
        return _lvgl.scale_get_mode(self)

    def get_total_tick_count(self) -> _lvgl.int32_t:
        return _lvgl.scale_get_total_tick_count(self)

    def get_major_tick_every(self) -> _lvgl.int32_t:
        return _lvgl.scale_get_major_tick_every(self)

    def get_rotation(self) -> _lvgl.int32_t:
        return _lvgl.scale_get_rotation(self)

    def get_label_show(self) -> _lvgl._Bool:
        return _lvgl.scale_get_label_show(self)

    def get_angle_range(self) -> _lvgl.uint32_t:
        return _lvgl.scale_get_angle_range(self)

    def get_range_min_value(self) -> _lvgl.int32_t:
        return _lvgl.scale_get_range_min_value(self)

    def get_range_max_value(self) -> _lvgl.int32_t:
        return _lvgl.scale_get_range_max_value(self)

    def bind_section_min_value(self, section: "scale_section_t", subject: "subject_t") -> "observer_t":
        return _lvgl.scale_bind_section_min_value(self, section, subject)

    def bind_section_max_value(self, section: "scale_section_t", subject: "subject_t") -> "observer_t":
        return _lvgl.scale_bind_section_max_value(self, section, subject)


class slider(obj):
    
    class MODE:
        NORMAL = _lvgl.SLIDER_MODE_NORMAL
        RANGE = _lvgl.SLIDER_MODE_RANGE
        SYMMETRICAL = _lvgl.SLIDER_MODE_SYMMETRICAL
    
    class ORIENTATION:
        AUTO = _lvgl.SLIDER_ORIENTATION_AUTO
        HORIZONTAL = _lvgl.SLIDER_ORIENTATION_HORIZONTAL
        VERTICAL = _lvgl.SLIDER_ORIENTATION_VERTICAL

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.slider_create(parent)
            cls.cast(self)


    def set_value(self, value: _lvgl.int32_t, anim: _lvgl.anim_enable_t) -> None:
        return _lvgl.slider_set_value(self, value, anim)

    def set_start_value(self, value: _lvgl.int32_t, anim: _lvgl.anim_enable_t) -> None:
        return _lvgl.slider_set_start_value(self, value, anim)

    def set_range(self, min: _lvgl.int32_t, max: _lvgl.int32_t) -> None:
        return _lvgl.slider_set_range(self, min, max)

    def set_min_value(self, min: _lvgl.int32_t) -> None:
        return _lvgl.slider_set_min_value(self, min)

    def set_max_value(self, max: _lvgl.int32_t) -> None:
        return _lvgl.slider_set_max_value(self, max)

    def set_mode(self, mode: _lvgl.slider_mode_t) -> None:
        return _lvgl.slider_set_mode(self, mode)

    def set_orientation(self, orientation: _lvgl.slider_orientation_t) -> None:
        return _lvgl.slider_set_orientation(self, orientation)

    def get_value(self) -> _lvgl.int32_t:
        return _lvgl.slider_get_value(self)

    def get_left_value(self) -> _lvgl.int32_t:
        return _lvgl.slider_get_left_value(self)

    def get_min_value(self) -> _lvgl.int32_t:
        return _lvgl.slider_get_min_value(self)

    def get_max_value(self) -> _lvgl.int32_t:
        return _lvgl.slider_get_max_value(self)

    def is_dragged(self) -> _lvgl._Bool:
        return _lvgl.slider_is_dragged(self)

    def get_mode(self) -> _lvgl.slider_mode_t:
        return _lvgl.slider_get_mode(self)

    def get_orientation(self) -> _lvgl.slider_orientation_t:
        return _lvgl.slider_get_orientation(self)

    def is_symmetrical(self) -> _lvgl._Bool:
        return _lvgl.slider_is_symmetrical(self)

    def bind_value(self, subject: "subject_t") -> "observer_t":
        return _lvgl.slider_bind_value(self, subject)


class spangroup(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.spangroup_create(parent)
            cls.cast(self)


    def add_span(self) -> "span_t":
        return _lvgl.spangroup_add_span(self)

    def delete_span(self, span: "span_t") -> None:
        return _lvgl.spangroup_delete_span(self, span)

    def set_span_text(self, span: "span_t", text: _lvgl.char) -> None:
        return _lvgl.spangroup_set_span_text(self, span, text)

    def set_span_text_static(self, span: "span_t", text: _lvgl.char) -> None:
        return _lvgl.spangroup_set_span_text_static(self, span, text)

    def set_span_text_fmt(self, span: "span_t", fmt: _lvgl.char, *args) -> None:
        return _lvgl.spangroup_set_span_text_fmt(self, span, fmt, *args)

    def set_span_style(self, span: "span_t", style: "style_t") -> None:
        return _lvgl.spangroup_set_span_style(self, span, style)

    def set_align(self, align: _lvgl.text_align_t) -> None:
        return _lvgl.spangroup_set_align(self, align)

    def set_overflow(self, overflow: _lvgl.span_overflow_t) -> None:
        return _lvgl.spangroup_set_overflow(self, overflow)

    def set_indent(self, indent: _lvgl.int32_t) -> None:
        return _lvgl.spangroup_set_indent(self, indent)

    def set_mode(self, mode: _lvgl.span_mode_t) -> None:
        return _lvgl.spangroup_set_mode(self, mode)

    def set_max_lines(self, lines: _lvgl.int32_t) -> None:
        return _lvgl.spangroup_set_max_lines(self, lines)

    def get_child(self, id: _lvgl.int32_t) -> "span_t":
        return _lvgl.spangroup_get_child(self, id)

    def get_span_count(self) -> _lvgl.uint32_t:
        return _lvgl.spangroup_get_span_count(self)

    def get_align(self) -> _lvgl.text_align_t:
        return _lvgl.spangroup_get_align(self)

    def get_overflow(self) -> _lvgl.span_overflow_t:
        return _lvgl.spangroup_get_overflow(self)

    def get_indent(self) -> _lvgl.int32_t:
        return _lvgl.spangroup_get_indent(self)

    def get_mode(self) -> _lvgl.span_mode_t:
        return _lvgl.spangroup_get_mode(self)

    def get_max_lines(self) -> _lvgl.int32_t:
        return _lvgl.spangroup_get_max_lines(self)

    def get_max_line_height(self) -> _lvgl.int32_t:
        return _lvgl.spangroup_get_max_line_height(self)

    def get_expand_width(self, max_width: _lvgl.uint32_t) -> _lvgl.uint32_t:
        return _lvgl.spangroup_get_expand_width(self, max_width)

    def get_expand_height(self, width: _lvgl.int32_t) -> _lvgl.int32_t:
        return _lvgl.spangroup_get_expand_height(self, width)

    def get_span_coords(self, span: "span_t") -> "span_coords_t":
        return _lvgl.spangroup_get_span_coords(self, span)

    def get_span_by_point(self, point: _lvgl.point_t) -> "span_t":
        return _lvgl.spangroup_get_span_by_point(self, point)

    def refresh(self) -> None:
        return _lvgl.spangroup_refresh(self)

    def bind_span_text(self, span: "span_t", subject: "subject_t", fmt: _lvgl.char) -> "observer_t":
        return _lvgl.spangroup_bind_span_text(self, span, subject, fmt)


class textarea(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.textarea_create(parent)
            cls.cast(self)


    def add_char(self, c: _lvgl.uint32_t) -> None:
        return _lvgl.textarea_add_char(self, c)

    def add_text(self, txt: _lvgl.char) -> None:
        return _lvgl.textarea_add_text(self, txt)

    def delete_char(self) -> None:
        return _lvgl.textarea_delete_char(self)

    def delete_char_forward(self) -> None:
        return _lvgl.textarea_delete_char_forward(self)

    def set_text(self, txt: _lvgl.char) -> None:
        return _lvgl.textarea_set_text(self, txt)

    def set_placeholder_text(self, txt: _lvgl.char) -> None:
        return _lvgl.textarea_set_placeholder_text(self, txt)

    def set_cursor_pos(self, pos: _lvgl.int32_t) -> None:
        return _lvgl.textarea_set_cursor_pos(self, pos)

    def set_cursor_click_pos(self, en: _lvgl._Bool) -> None:
        return _lvgl.textarea_set_cursor_click_pos(self, en)

    def set_password_mode(self, en: _lvgl._Bool) -> None:
        return _lvgl.textarea_set_password_mode(self, en)

    def set_password_bullet(self, bullet: _lvgl.char) -> None:
        return _lvgl.textarea_set_password_bullet(self, bullet)

    def set_one_line(self, en: _lvgl._Bool) -> None:
        return _lvgl.textarea_set_one_line(self, en)

    def set_accepted_chars(self, list: _lvgl.char) -> None:
        return _lvgl.textarea_set_accepted_chars(self, list)

    def set_accepted_chars_static(self, list: _lvgl.char) -> None:
        return _lvgl.textarea_set_accepted_chars_static(self, list)

    def set_max_length(self, num: _lvgl.uint32_t) -> None:
        return _lvgl.textarea_set_max_length(self, num)

    def set_insert_replace(self, txt: _lvgl.char) -> None:
        return _lvgl.textarea_set_insert_replace(self, txt)

    def set_text_selection(self, en: _lvgl._Bool) -> None:
        return _lvgl.textarea_set_text_selection(self, en)

    def set_password_show_time(self, time: _lvgl.uint32_t) -> None:
        return _lvgl.textarea_set_password_show_time(self, time)

    def set_align(self, align: _lvgl.text_align_t) -> None:
        return _lvgl.textarea_set_align(self, align)

    def get_text(self) -> _lvgl.char:
        return _lvgl.textarea_get_text(self)

    def get_placeholder_text(self) -> _lvgl.char:
        return _lvgl.textarea_get_placeholder_text(self)

    def get_label(self) -> "obj":
        return _wrap_obj(_lvgl.textarea_get_label(self))

    def get_cursor_pos(self) -> _lvgl.uint32_t:
        return _lvgl.textarea_get_cursor_pos(self)

    def get_cursor_click_pos(self) -> _lvgl._Bool:
        return _lvgl.textarea_get_cursor_click_pos(self)

    def get_password_mode(self) -> _lvgl._Bool:
        return _lvgl.textarea_get_password_mode(self)

    def get_password_bullet(self) -> _lvgl.char:
        return _lvgl.textarea_get_password_bullet(self)

    def get_one_line(self) -> _lvgl._Bool:
        return _lvgl.textarea_get_one_line(self)

    def get_accepted_chars(self) -> _lvgl.char:
        return _lvgl.textarea_get_accepted_chars(self)

    def get_max_length(self) -> _lvgl.uint32_t:
        return _lvgl.textarea_get_max_length(self)

    def text_is_selected(self) -> _lvgl._Bool:
        return _lvgl.textarea_text_is_selected(self)

    def get_text_selection(self) -> _lvgl._Bool:
        return _lvgl.textarea_get_text_selection(self)

    def get_password_show_time(self) -> _lvgl.uint32_t:
        return _lvgl.textarea_get_password_show_time(self)

    def get_current_char(self) -> _lvgl.uint32_t:
        return _lvgl.textarea_get_current_char(self)

    def clear_selection(self) -> None:
        return _lvgl.textarea_clear_selection(self)

    def cursor_right(self) -> None:
        return _lvgl.textarea_cursor_right(self)

    def cursor_left(self) -> None:
        return _lvgl.textarea_cursor_left(self)

    def cursor_down(self) -> None:
        return _lvgl.textarea_cursor_down(self)

    def cursor_up(self) -> None:
        return _lvgl.textarea_cursor_up(self)


class spinbox(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.spinbox_create(parent)
            cls.cast(self)


    def set_value(self, v: _lvgl.int32_t) -> None:
        return _lvgl.spinbox_set_value(self, v)

    def set_rollover(self, rollover: _lvgl._Bool) -> None:
        return _lvgl.spinbox_set_rollover(self, rollover)

    def set_digit_format(self, digit_count: _lvgl.uint32_t, sep_pos: _lvgl.uint32_t) -> None:
        return _lvgl.spinbox_set_digit_format(self, digit_count, sep_pos)

    def set_digit_count(self, digit_count: _lvgl.uint32_t) -> None:
        return _lvgl.spinbox_set_digit_count(self, digit_count)

    def set_dec_point_pos(self, dec_point_pos: _lvgl.uint32_t) -> None:
        return _lvgl.spinbox_set_dec_point_pos(self, dec_point_pos)

    def set_step(self, step: _lvgl.uint32_t) -> None:
        return _lvgl.spinbox_set_step(self, step)

    def set_range(self, min_value: _lvgl.int32_t, max_value: _lvgl.int32_t) -> None:
        return _lvgl.spinbox_set_range(self, min_value, max_value)

    def set_min_value(self, min_value: _lvgl.int32_t) -> None:
        return _lvgl.spinbox_set_min_value(self, min_value)

    def set_max_value(self, max_value: _lvgl.int32_t) -> None:
        return _lvgl.spinbox_set_max_value(self, max_value)

    def set_cursor_pos(self, pos: _lvgl.uint32_t) -> None:
        return _lvgl.spinbox_set_cursor_pos(self, pos)

    def set_digit_step_direction(self, direction: _lvgl.dir_t) -> None:
        return _lvgl.spinbox_set_digit_step_direction(self, direction)

    def get_rollover(self) -> _lvgl._Bool:
        return _lvgl.spinbox_get_rollover(self)

    def get_value(self) -> _lvgl.int32_t:
        return _lvgl.spinbox_get_value(self)

    def get_step(self) -> _lvgl.int32_t:
        return _lvgl.spinbox_get_step(self)

    def get_digit_count(self) -> _lvgl.uint32_t:
        return _lvgl.spinbox_get_digit_count(self)

    def get_dec_point_pos(self) -> _lvgl.uint32_t:
        return _lvgl.spinbox_get_dec_point_pos(self)

    def get_min_value(self) -> _lvgl.int32_t:
        return _lvgl.spinbox_get_min_value(self)

    def get_max_value(self) -> _lvgl.int32_t:
        return _lvgl.spinbox_get_max_value(self)

    def get_digit_step_direction(self) -> _lvgl.dir_t:
        return _lvgl.spinbox_get_digit_step_direction(self)

    def step_next(self) -> None:
        return _lvgl.spinbox_step_next(self)

    def step_prev(self) -> None:
        return _lvgl.spinbox_step_prev(self)

    def increment(self) -> None:
        return _lvgl.spinbox_increment(self)

    def decrement(self) -> None:
        return _lvgl.spinbox_decrement(self)

    def bind_value(self, subject: "subject_t") -> "observer_t":
        return _lvgl.spinbox_bind_value(self, subject)


class spinner(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.spinner_create(parent)
            cls.cast(self)


    def set_anim_params(self, t: _lvgl.uint32_t, angle: _lvgl.uint32_t) -> None:
        return _lvgl.spinner_set_anim_params(self, t, angle)

    def set_anim_duration(self, t: _lvgl.uint32_t) -> None:
        return _lvgl.spinner_set_anim_duration(self, t)

    def set_arc_sweep(self, angle: _lvgl.uint32_t) -> None:
        return _lvgl.spinner_set_arc_sweep(self, angle)

    def get_anim_duration(self) -> _lvgl.uint32_t:
        return _lvgl.spinner_get_anim_duration(self)

    def get_arc_sweep(self) -> _lvgl.uint32_t:
        return _lvgl.spinner_get_arc_sweep(self)


class switch(obj):
    
    class ORIENTATION:
        AUTO = _lvgl.SWITCH_ORIENTATION_AUTO
        HORIZONTAL = _lvgl.SWITCH_ORIENTATION_HORIZONTAL
        VERTICAL = _lvgl.SWITCH_ORIENTATION_VERTICAL

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.switch_create(parent)
            cls.cast(self)


    def set_orientation(self, orientation: _lvgl.switch_orientation_t) -> None:
        return _lvgl.switch_set_orientation(self, orientation)

    def get_orientation(self) -> _lvgl.switch_orientation_t:
        return _lvgl.switch_get_orientation(self)


class table(obj):
    
    class CELL_CTRL:
        CUSTOM_1 = _lvgl.TABLE_CELL_CTRL_CUSTOM_1
        CUSTOM_2 = _lvgl.TABLE_CELL_CTRL_CUSTOM_2
        CUSTOM_3 = _lvgl.TABLE_CELL_CTRL_CUSTOM_3
        CUSTOM_4 = _lvgl.TABLE_CELL_CTRL_CUSTOM_4
        MERGE_RIGHT = _lvgl.TABLE_CELL_CTRL_MERGE_RIGHT
        NONE = _lvgl.TABLE_CELL_NONE
        TEXT_CROP = _lvgl.TABLE_CELL_CTRL_TEXT_CROP

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.table_create(parent)
            cls.cast(self)


    def set_cell_value(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t, txt: _lvgl.char) -> None:
        return _lvgl.table_set_cell_value(self, row, col, txt)

    def set_cell_value_fmt(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t, fmt: _lvgl.char, *args) -> None:
        return _lvgl.table_set_cell_value_fmt(self, row, col, fmt, *args)

    def set_row_count(self, row_cnt: _lvgl.uint32_t) -> None:
        return _lvgl.table_set_row_count(self, row_cnt)

    def set_column_count(self, col_cnt: _lvgl.uint32_t) -> None:
        return _lvgl.table_set_column_count(self, col_cnt)

    def set_column_width(self, col_id: _lvgl.uint32_t, w: _lvgl.int32_t) -> None:
        return _lvgl.table_set_column_width(self, col_id, w)

    def set_cell_ctrl(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t, ctrl: _lvgl.table_cell_ctrl_t) -> None:
        return _lvgl.table_set_cell_ctrl(self, row, col, ctrl)

    def clear_cell_ctrl(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t, ctrl: _lvgl.table_cell_ctrl_t) -> None:
        return _lvgl.table_clear_cell_ctrl(self, row, col, ctrl)

    def set_cell_user_data(self, row: _lvgl.uint16_t, col: _lvgl.uint16_t, user_data: "Any") -> None:
        return _lvgl.table_set_cell_user_data(self, row, col, user_data)

    def set_selected_cell(self, row: _lvgl.uint16_t, col: _lvgl.uint16_t) -> None:
        return _lvgl.table_set_selected_cell(self, row, col)

    def get_cell_value(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t) -> _lvgl.char:
        return _lvgl.table_get_cell_value(self, row, col)

    def get_row_count(self) -> _lvgl.uint32_t:
        return _lvgl.table_get_row_count(self)

    def get_column_count(self) -> _lvgl.uint32_t:
        return _lvgl.table_get_column_count(self)

    def get_column_width(self, col: _lvgl.uint32_t) -> _lvgl.int32_t:
        return _lvgl.table_get_column_width(self, col)

    def has_cell_ctrl(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t, ctrl: _lvgl.table_cell_ctrl_t) -> _lvgl._Bool:
        return _lvgl.table_has_cell_ctrl(self, row, col, ctrl)

    def get_selected_cell(self, row: _lvgl.uint32_t, col: _lvgl.uint32_t) -> None:
        return _lvgl.table_get_selected_cell(self, row, col)

    def get_cell_user_data(self, row: _lvgl.uint16_t, col: _lvgl.uint16_t) -> "Any":
        return _lvgl.table_get_cell_user_data(self, row, col)


class tabview(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.tabview_create(parent)
            cls.cast(self)


    def add_tab(self, name: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.tabview_add_tab(self, name))

    def set_tab_text(self, idx: _lvgl.uint32_t, new_name: _lvgl.char) -> None:
        return _lvgl.tabview_set_tab_text(self, idx, new_name)

    def set_active(self, idx: _lvgl.uint32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.tabview_set_active(self, idx, anim_en)

    def set_tab_bar_position(self, dir: _lvgl.dir_t) -> None:
        return _lvgl.tabview_set_tab_bar_position(self, dir)

    def set_tab_bar_size(self, size: _lvgl.int32_t) -> None:
        return _lvgl.tabview_set_tab_bar_size(self, size)

    def get_tab_count(self) -> _lvgl.uint32_t:
        return _lvgl.tabview_get_tab_count(self)

    def get_tab_active(self) -> _lvgl.uint32_t:
        return _lvgl.tabview_get_tab_active(self)

    def get_tab_button(self, idx: _lvgl.int32_t) -> "obj":
        return _wrap_obj(_lvgl.tabview_get_tab_button(self, idx))

    def get_content(self) -> "obj":
        return _wrap_obj(_lvgl.tabview_get_content(self))

    def get_tab_bar(self) -> "obj":
        return _wrap_obj(_lvgl.tabview_get_tab_bar(self))

    def get_tab_bar_position(self) -> _lvgl.dir_t:
        return _lvgl.tabview_get_tab_bar_position(self)


class tileview(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.tileview_create(parent)
            cls.cast(self)


    def add_tile(self, col_id: _lvgl.uint8_t, row_id: _lvgl.uint8_t, dir: _lvgl.dir_t) -> "obj":
        return _wrap_obj(_lvgl.tileview_add_tile(self, col_id, row_id, dir))

    def set_tile(self, tile_obj: "obj", anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.tileview_set_tile(self, tile_obj, anim_en)

    def set_tile_by_index(self, col_id: _lvgl.uint32_t, row_id: _lvgl.uint32_t, anim_en: _lvgl.anim_enable_t) -> None:
        return _lvgl.tileview_set_tile_by_index(self, col_id, row_id, anim_en)

    def get_tile_active(self) -> "obj":
        return _wrap_obj(_lvgl.tileview_get_tile_active(self))


class win(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.win_create(parent)
            cls.cast(self)


    def add_title(self, txt: _lvgl.char) -> "obj":
        return _wrap_obj(_lvgl.win_add_title(self, txt))

    def add_button(self, icon: None, btn_w: _lvgl.int32_t) -> "obj":
        return _wrap_obj(_lvgl.win_add_button(self, icon, btn_w))

    def get_header(self) -> "obj":
        return _wrap_obj(_lvgl.win_get_header(self))

    def get_content(self) -> "obj":
        return _wrap_obj(_lvgl.win_get_content(self))


class ime_pinyin(obj):
    
    class MODE:
        K26 = _lvgl.IME_PINYIN_MODE_K26
        K9 = _lvgl.IME_PINYIN_MODE_K9
        K9_NUMBER = _lvgl.IME_PINYIN_MODE_K9_NUMBER

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.ime_pinyin_create(parent)
            cls.cast(self)


    def set_keyboard(self, kb: "obj") -> None:
        return _lvgl.ime_pinyin_set_keyboard(self, kb)

    def set_dict(self, dict: "pinyin_dict_t") -> None:
        return _lvgl.ime_pinyin_set_dict(self, dict)

    def set_mode(self, mode: _lvgl.ime_pinyin_mode_t) -> None:
        return _lvgl.ime_pinyin_set_mode(self, mode)

    def get_kb(self) -> "obj":
        return _wrap_obj(_lvgl.ime_pinyin_get_kb(self))

    def get_cand_panel(self) -> "obj":
        return _wrap_obj(_lvgl.ime_pinyin_get_cand_panel(self))

    def get_dict(self) -> "pinyin_dict_t":
        return _lvgl.ime_pinyin_get_dict(self)


class file_explorer(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.file_explorer_create(parent)
            cls.cast(self)


    def set_quick_access_path(self, dir: _lvgl.file_explorer_dir_t, path: _lvgl.char) -> None:
        return _lvgl.file_explorer_set_quick_access_path(self, dir, path)

    def set_sort(self, sort: _lvgl.file_explorer_sort_t) -> None:
        return _lvgl.file_explorer_set_sort(self, sort)

    def show_back_button(self, show: _lvgl._Bool) -> None:
        return _lvgl.file_explorer_show_back_button(self, show)

    def get_selected_file_name(self) -> _lvgl.char:
        return _lvgl.file_explorer_get_selected_file_name(self)

    def get_current_path(self) -> _lvgl.char:
        return _lvgl.file_explorer_get_current_path(self)

    def get_file_table(self) -> "obj":
        return _wrap_obj(_lvgl.file_explorer_get_file_table(self))

    def get_header(self) -> "obj":
        return _wrap_obj(_lvgl.file_explorer_get_header(self))

    def get_path_label(self) -> "obj":
        return _wrap_obj(_lvgl.file_explorer_get_path_label(self))

    def get_quick_access_area(self) -> "obj":
        return _wrap_obj(_lvgl.file_explorer_get_quick_access_area(self))

    def get_places_list(self) -> "obj":
        return _wrap_obj(_lvgl.file_explorer_get_places_list(self))

    def get_device_list(self) -> "obj":
        return _wrap_obj(_lvgl.file_explorer_get_device_list(self))

    def get_sort(self) -> _lvgl.file_explorer_sort_t:
        return _lvgl.file_explorer_get_sort(self)

    def open_dir(self, dir: _lvgl.char) -> None:
        return _lvgl.file_explorer_open_dir(self, dir)


class barcode(obj):
    
    class ENCODING_CODE128:
        GS1 = _lvgl.BARCODE_ENCODING_CODE128_GS1
        RAW = _lvgl.BARCODE_ENCODING_CODE128_RAW

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.barcode_create(parent)
            cls.cast(self)


    def set_dark_color(self, color: "color_t") -> None:
        return _lvgl.barcode_set_dark_color(self, color)

    def set_light_color(self, color: "color_t") -> None:
        return _lvgl.barcode_set_light_color(self, color)

    def set_scale(self, scale: _lvgl.uint16_t) -> None:
        return _lvgl.barcode_set_scale(self, scale)

    def set_direction(self, direction: _lvgl.dir_t) -> None:
        return _lvgl.barcode_set_direction(self, direction)

    def set_tiled(self, tiled: _lvgl._Bool) -> None:
        return _lvgl.barcode_set_tiled(self, tiled)

    def set_encoding(self, encoding: _lvgl.barcode_encoding_t) -> None:
        return _lvgl.barcode_set_encoding(self, encoding)

    def update(self, data: _lvgl.char) -> _lvgl.result_t:
        return _lvgl.barcode_update(self, data)

    def get_dark_color(self) -> "color_t":
        return _lvgl.barcode_get_dark_color(self)

    def get_light_color(self) -> "color_t":
        return _lvgl.barcode_get_light_color(self)

    def get_scale(self) -> _lvgl.uint16_t:
        return _lvgl.barcode_get_scale(self)

    def get_encoding(self) -> _lvgl.barcode_encoding_t:
        return _lvgl.barcode_get_encoding(self)


class qrcode(obj):

    def __init__(self, parent: _lvgl.obj_t = None):
        for arg in (parent,):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.qrcode_create(parent)
            cls.cast(self)


    def set_size(self, size: _lvgl.int32_t) -> None:
        return _lvgl.qrcode_set_size(self, size)

    def set_dark_color(self, color: "color_t") -> None:
        return _lvgl.qrcode_set_dark_color(self, color)

    def set_light_color(self, color: "color_t") -> None:
        return _lvgl.qrcode_set_light_color(self, color)

    def update(self, data: None, data_len: _lvgl.uint32_t) -> _lvgl.result_t:
        return _lvgl.qrcode_update(self, data, data_len)

    def set_data(self, data: _lvgl.char) -> None:
        return _lvgl.qrcode_set_data(self, data)

    def set_quiet_zone(self, enable: _lvgl._Bool) -> None:
        return _lvgl.qrcode_set_quiet_zone(self, enable)



_obj_type_map = []
if hasattr(_lvgl, 'draw_layer_class'):
    _obj_type_map.append((_lvgl.draw_layer_class, draw_layer))
if hasattr(_lvgl, 'image_class'):
    _obj_type_map.append((_lvgl.image_class, image))
if hasattr(_lvgl, 'animimg_class'):
    _obj_type_map.append((_lvgl.animimg_class, animimg))
if hasattr(_lvgl, 'arc_class'):
    _obj_type_map.append((_lvgl.arc_class, arc))
if hasattr(_lvgl, 'arclabel_class'):
    _obj_type_map.append((_lvgl.arclabel_class, arclabel))
if hasattr(_lvgl, 'label_class'):
    _obj_type_map.append((_lvgl.label_class, label))
if hasattr(_lvgl, 'bar_class'):
    _obj_type_map.append((_lvgl.bar_class, bar))
if hasattr(_lvgl, 'button_class'):
    _obj_type_map.append((_lvgl.button_class, button))
if hasattr(_lvgl, 'buttonmatrix_class'):
    _obj_type_map.append((_lvgl.buttonmatrix_class, buttonmatrix))
if hasattr(_lvgl, 'calendar_class'):
    _obj_type_map.append((_lvgl.calendar_class, calendar))
if hasattr(_lvgl, 'canvas_class'):
    _obj_type_map.append((_lvgl.canvas_class, canvas))
if hasattr(_lvgl, 'chart_class'):
    _obj_type_map.append((_lvgl.chart_class, chart))
if hasattr(_lvgl, 'checkbox_class'):
    _obj_type_map.append((_lvgl.checkbox_class, checkbox))
if hasattr(_lvgl, 'dropdown_class'):
    _obj_type_map.append((_lvgl.dropdown_class, dropdown))
if hasattr(_lvgl, 'gif_class'):
    _obj_type_map.append((_lvgl.gif_class, gif))
if hasattr(_lvgl, 'imagebutton_class'):
    _obj_type_map.append((_lvgl.imagebutton_class, imagebutton))
if hasattr(_lvgl, 'keyboard_class'):
    _obj_type_map.append((_lvgl.keyboard_class, keyboard))
if hasattr(_lvgl, 'led_class'):
    _obj_type_map.append((_lvgl.led_class, led))
if hasattr(_lvgl, 'line_class'):
    _obj_type_map.append((_lvgl.line_class, line))
if hasattr(_lvgl, 'list_class'):
    _obj_type_map.append((_lvgl.list_class, list))
if hasattr(_lvgl, 'menu_class'):
    _obj_type_map.append((_lvgl.menu_class, menu))
if hasattr(_lvgl, 'menu_page_class'):
    _obj_type_map.append((_lvgl.menu_page_class, menu_page))
if hasattr(_lvgl, 'menu_cont_class'):
    _obj_type_map.append((_lvgl.menu_cont_class, menu_cont))
if hasattr(_lvgl, 'menu_section_class'):
    _obj_type_map.append((_lvgl.menu_section_class, menu_section))
if hasattr(_lvgl, 'menu_separator_class'):
    _obj_type_map.append((_lvgl.menu_separator_class, menu_separator))
if hasattr(_lvgl, 'msgbox_class'):
    _obj_type_map.append((_lvgl.msgbox_class, msgbox))
if hasattr(_lvgl, 'roller_class'):
    _obj_type_map.append((_lvgl.roller_class, roller))
if hasattr(_lvgl, 'scale_class'):
    _obj_type_map.append((_lvgl.scale_class, scale))
if hasattr(_lvgl, 'slider_class'):
    _obj_type_map.append((_lvgl.slider_class, slider))
if hasattr(_lvgl, 'spangroup_class'):
    _obj_type_map.append((_lvgl.spangroup_class, spangroup))
if hasattr(_lvgl, 'textarea_class'):
    _obj_type_map.append((_lvgl.textarea_class, textarea))
if hasattr(_lvgl, 'spinbox_class'):
    _obj_type_map.append((_lvgl.spinbox_class, spinbox))
if hasattr(_lvgl, 'spinner_class'):
    _obj_type_map.append((_lvgl.spinner_class, spinner))
if hasattr(_lvgl, 'switch_class'):
    _obj_type_map.append((_lvgl.switch_class, switch))
if hasattr(_lvgl, 'table_class'):
    _obj_type_map.append((_lvgl.table_class, table))
if hasattr(_lvgl, 'tabview_class'):
    _obj_type_map.append((_lvgl.tabview_class, tabview))
if hasattr(_lvgl, 'tileview_class'):
    _obj_type_map.append((_lvgl.tileview_class, tileview))
if hasattr(_lvgl, 'win_class'):
    _obj_type_map.append((_lvgl.win_class, win))
if hasattr(_lvgl, 'ime_pinyin_class'):
    _obj_type_map.append((_lvgl.ime_pinyin_class, ime_pinyin))
if hasattr(_lvgl, 'file_explorer_class'):
    _obj_type_map.append((_lvgl.file_explorer_class, file_explorer))
if hasattr(_lvgl, 'barcode_class'):
    _obj_type_map.append((_lvgl.barcode_class, barcode))
if hasattr(_lvgl, 'qrcode_class'):
    _obj_type_map.append((_lvgl.qrcode_class, qrcode))
if hasattr(_lvgl, "obj_class"):
    _obj_type_map.append((_lvgl.obj_class, obj))


def _wrap_obj(value):
    if value is None:
        return None

    for lv_class, py_class in _obj_type_map:
        try:
            if _lvgl.obj_check_type(value, lv_class):
                instance = object.__new__(py_class)
                value.cast(instance)
                return instance
        except Exception:
            continue

    return value


# MicroPython lv_font_t function-pointer compatibility
def _font_get_glyph_dsc_field(self, font, dsc, letter, letter_next):
    c_func = self._obj.get_glyph_dsc

    if c_func == _lvgl._lib_lvgl.ffi.NULL:
        return False

    return bool(
        c_func(
            font._obj,
            dsc._obj,
            letter,
            letter_next,
        )
    )


_lvgl.font_t.get_glyph_dsc = _font_get_glyph_dsc_field
font_t.get_glyph_dsc = _font_get_glyph_dsc_field
del _font_get_glyph_dsc_field


def _obj_set_grid_dsc_array(self, col_dsc, row_dsc):
    col_ref = _lvgl._make_c_array([int(value) for value in col_dsc], 'List[int32_t]')
    row_ref = _lvgl._make_c_array([int(value) for value in row_dsc], 'List[int32_t]')
    result = _lvgl.obj_set_grid_dsc_array(self, col_ref, row_ref)
    _retain_obj_ref(self, 'grid_columns', col_ref, append=False)
    _retain_obj_ref(self, 'grid_rows', row_ref, append=False)
    return result


obj.set_grid_dsc_array = _obj_set_grid_dsc_array
del _obj_set_grid_dsc_array


# Button-matrix map lifetime compatibility
def _buttonmatrix_set_map(self, map):
    map_ref = _lvgl._make_c_array(
        map,
        'List[char *]',
    )

    result = _lvgl.buttonmatrix_set_map(self, map_ref)
    _retain_obj_ref(self, 'buttonmatrix_map', map_ref, append=False)
    return result


buttonmatrix.set_map = _buttonmatrix_set_map
del _buttonmatrix_set_map


# Keyboard map lifetime compatibility
def _keyboard_set_map(self, mode, map, ctrl_map):
    map_ref = _lvgl._make_c_array(
        map,
        'List[char *]',
    )

    ctrl_map_ref = _lvgl._make_c_array(
        ctrl_map,
        'List[buttonmatrix_ctrl_t]',
    )

    mode_key = int(mode)

    result = _lvgl.keyboard_set_map(
        self,
        mode,
        map_ref,
        ctrl_map_ref,
    )

    _retain_obj_ref(
        self,
        f'keyboard_map_{mode_key}',
        map_ref,
        append=False,
    )

    _retain_obj_ref(
        self,
        f'keyboard_ctrl_map_{mode_key}',
        ctrl_map_ref,
        append=False,
    )
    return result


keyboard.set_map = _keyboard_set_map
del _keyboard_set_map


def _event_get_user_data(self):
    value = _lvgl.event_get_user_data(self)

    if hasattr(value, '__cast__'):
        value = value.__cast__()

    elif hasattr(value, '_obj'):
        value = _lvgl._lib_lvgl.ffi.from_handle(
            _lvgl._lib_lvgl.ffi.cast('void *', value._obj)
        )

    if isinstance(value, dict) and 'user_data' in value:
        return value['user_data']

    return value


event_t.get_user_data = _event_get_user_data
del _event_get_user_data



# Animation path callbacks
anim_t.path_bounce = staticmethod(anim_path_bounce)
anim_t.path_custom_bezier3 = staticmethod(anim_path_custom_bezier3)
anim_t.path_ease_in = staticmethod(anim_path_ease_in)
anim_t.path_ease_in_out = staticmethod(anim_path_ease_in_out)
anim_t.path_ease_out = staticmethod(anim_path_ease_out)
anim_t.path_linear = staticmethod(anim_path_linear)
anim_t.path_overshoot = staticmethod(anim_path_overshoot)
anim_t.path_step = staticmethod(anim_path_step)
