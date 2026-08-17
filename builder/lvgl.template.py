from typing import Union, Any, Callable, Optional, List  # NOQA

try:
    from . import __lib_lvgl as _lib_lvgl  # NOQA
except ImportError:
    import __lib_lvgl as _lib_lvgl  # NOQA

_MPY_API = False

# Keep CFFI allocations and opaque handles returned from Python callbacks
# alive while LVGL may retain the corresponding C pointer.
_callback_object_handles = {}

def _make_callback_object_handle(py_obj):
    # Return a stable void * handle for an arbitrary Python callback result.
    #
    # LVGL APIs such as lv_fs_drv_t.open_cb store the returned pointer and
    # pass it back to later callbacks. ffi.new_handle() provides the opaque
    # pointer; this registry keeps the handle cdata alive while LVGL owns it.
    handle = _lib_lvgl.ffi.new_handle(py_obj)
    key = int(_lib_lvgl.ffi.cast('uintptr_t', handle))
    _callback_object_handles[key] = handle
    return handle


def _release_callback_object_handle(c_obj):
    # Release a handle previously created by _make_callback_object_handle().
    if c_obj is None or c_obj == _lib_lvgl.ffi.NULL:
        return

    key = int(
        _lib_lvgl.ffi.cast(
            'uintptr_t',
            _lib_lvgl.ffi.cast('void *', c_obj),
        )
    )
    _callback_object_handles.pop(key, None)


__version__ = "0.1.2"


def binding_version():
    return __version__

def sdl_get_display_size(display_index: int = 0):
    """Return current SDL display resolution as (width, height)."""

    width = _lib_lvgl.ffi.new('int *')
    height = _lib_lvgl.ffi.new('int *')

    result = _lib_lvgl.lib.py_sdl_get_display_size(
        int(display_index),
        width,
        height,
    )

    if result != 0:
        error = _lib_lvgl.lib.py_sdl_get_error()

        if error == _lib_lvgl.ffi.NULL:
            message = "unknown SDL error"
        else:
            message = _lib_lvgl.ffi.string(error).decode(
                "utf-8",
                errors="replace",
            )

        raise RuntimeError(
            f"unable to query SDL display {display_index}: "
            f"{message}"
        )

    return int(width[0]), int(height[0])

def _get_py_obj(c_obj, c_type):
    if c_type == 'None':
        return None

    if c_obj == _lib_lvgl.ffi.NULL:
        return None

    # CFFI represents scalar char as bytes of length 1.
    # MicroPython LVGL represents scalar char fields as integer values.
    if c_type == 'char' and isinstance(c_obj, bytes):
        if len(c_obj) != 1:
            raise ValueError(
                f'expected scalar char, got {len(c_obj)} bytes'
            )
        return c_obj[0]

    # The generator currently flattens `const char *` return types to
    # `char`.  Distinguish an actual C char pointer/array from a scalar
    # char by inspecting the CFFI object and convert C strings to Python
    # str.  LVGL strings are UTF-8 and remain owned by LVGL.
    if c_type == 'char' and not isinstance(
        c_obj,
        (int, float, str, bytes),
    ):
        try:
            char_type = _lib_lvgl.ffi.typeof(c_obj)

            if (
                char_type.kind in ('pointer', 'array')
                and char_type.item.kind == 'primitive'
                and char_type.item.cname == 'char'
            ):
                return _lib_lvgl.ffi.string(c_obj).decode('utf-8')
        except (TypeError, AttributeError):  # NOQA
            pass

    if not isinstance(c_obj, (int, float, str, bytes)):
        type_ = _lib_lvgl.ffi.typeof(c_obj)

        while type_.kind == 'pointer':
            type_ = type_.item

        if type_.kind == 'array':
            # not used at the moment, need to find a way to test it
            size = type_.length  # NOQA

        if c_type.lower().startswith('list'):
            c_type = c_type.split('[')[-1][:-1]
            cls = type(c_type + '[]', (_Array,), {'_c_obj': c_type})
            instance = cls()
            instance._obj = c_obj

            return instance

    glob = globals()

    if c_type in glob:
        cls = glob[c_type]

        if issubclass(cls, _StructUnion):
            cls = _StructUnionMeta.get_wrapper(cls)

            # Object already exists in C. Do not run __init__, which would
            # allocate another C object.
            instance = object.__new__(cls)
            instance._obj = c_obj
            return instance

        cls = type(c_type, (cls,), {'_obj': c_obj, '_c_type': c_type + ' *'})
        res = cls(c_obj)

        return res

    if c_type + '_' in glob:
        cls = glob[c_type + '_']

        if issubclass(cls, _StructUnion):
            cls = _StructUnionMeta.get_wrapper(cls)

            # Object already exists in C. Do not run __init__, which would
            # allocate another C object.
            instance = object.__new__(cls)
            instance._obj = c_obj
            return instance

        cls = type(c_type, (cls,), {'_obj': c_obj, '_c_type': c_type + ' *'})
        res = cls(c_obj)

        return res

    if isinstance(c_obj, bool):
        return _convert_basic_type(c_obj, c_type)

    if isinstance(c_obj, (int, float)):
        return _convert_basic_type(c_obj, c_type)

    if c_type is None:
        try:
            c_type = _get_c_type(c_obj)
        except Exception:  # NOQA
            return c_obj

    try:
        _ = c_obj[0]

        cls = type(c_type, (_Array,), {'_c_type': c_type})
        array = cls()
        array._obj = c_obj  # NOQA
        return array
    except Exception:  # NOQA
        pass

    return c_obj

def _make_c_array(py_obj, c_type):
    if isinstance(py_obj, _Array):
        return py_obj

    if c_type.startswith('List'):
        c_type = c_type.split('[', 1)[1][:-1]

    cls = type(
        f'{c_type}[]',
        (_Array,),
        {'_c_type': c_type},
    )

    instance = cls()

    # Scalar/struct arrays need their Python values converted to wrappers.
    # Pointer arrays, especially char *[], must remain as Python objects
    # until _Array materialises their actual pointers.
    if '*' not in c_type:
        type_cls = globals()[c_type]
        py_obj = list(py_obj)

        for i, item in enumerate(py_obj):
            if hasattr(item, '_obj'):
                continue

            py_obj[i] = (
                type_cls(**item)
                if isinstance(item, dict)
                else type_cls(item)
            )

    instance.extend(py_obj)

    # Force materialisation while the owner exists.
    _ = instance._obj

    return instance


def _get_c_obj(py_obj, c_type):
    if isinstance(py_obj, dict):
        return py_obj

    if py_obj is None:
        return _lib_lvgl.ffi.NULL

    # CFFI does not implicitly convert Python buffer objects to void *.
    # LVGL APIs such as lv_canvas_set_buffer() accept a raw buffer pointer.
    # The generator currently reports void * parameters as 'None', so also
    # accept that spelling here until pointer depth is preserved by the
    # generator.
    if (
        c_type in ('None', 'Any', 'void', 'void *')
        and isinstance(py_obj, (bytes, bytearray, memoryview))
    ):
        return _lib_lvgl.ffi.from_buffer(py_obj)

    if c_type == 'char':
        # Scalar C char. MicroPython API commonly supplies ord(...).
        if isinstance(py_obj, int):
            if not 0 <= py_obj <= 255:
                raise ValueError(
                    f'char integer must be in range 0..255, got {py_obj}'
                )

            return bytes((py_obj,))

        # The generator currently also reports char * as "char".
        # Strings therefore must not be restricted to one byte.
        if isinstance(py_obj, str):
            return py_obj.encode('utf-8')

        if isinstance(py_obj, (bytes, bytearray)):
            return bytes(py_obj)

    if hasattr(py_obj, '_obj'):
        return py_obj._obj  # NOQA

    if c_type is not None:
        globs = globals()

        if c_type.startswith('List'):
            return _make_c_array(py_obj, c_type)._obj

        def _instance(_c_type):
            c = globs[_c_type]

            try:
                if isinstance(py_obj, dict):
                    ins = c(**py_obj)
                else:
                    ins = c(py_obj)

                return ins._obj  # NOQA
            except Exception:  # NOQA
                pass


        if c_type in globs:
            obj = _instance(c_type)
            if obj is not None:
                return obj

        if f'{c_type}_' in globs:
            obj = _instance(f'{c_type}_')
            if obj is not None:
                return obj

    if isinstance(py_obj, (int, float)):
        return py_obj
    if isinstance(py_obj, str):
        return py_obj.encode('utf-8')

    if isinstance(py_obj, tuple):
        py_obj = list(py_obj)

    return [py_obj] if isinstance(py_obj, list) else py_obj


def _get_c_type(c_obj):
    if isinstance(c_obj, int):
        return None

    cdata = str(_lib_lvgl.ffi.typeof(c_obj)).replace("'", '')
    c_type = ''

    for itm in cdata.split(' '):
        if '*' in itm:
            break

        c_type = itm

    c_type = c_type.replace('>', '')

    return c_type.replace('struct', '').replace('union', '').strip()


class _CBStore(dict):
    pass


class va_list(list):
    pass


class _DefaultArg:
    pass

class _CallbackPointer:
    def __init__(self, c_obj, c_type='void'):
        self._obj = c_obj
        self._c_type = c_type

    def __cast__(self):
        """Recover a Python object stored using ffi.new_handle()."""
        return _lib_lvgl.ffi.from_handle(
            _lib_lvgl.ffi.cast('void *', self._obj)
        )

    def __dereference__(self, size=None):
        """Expose pointed memory using MicroPython LVGL semantics."""
        if size is None:
            try:
                return _get_py_obj(self._obj[0], self._c_type)
            except Exception:
                size = _lib_lvgl.ffi.sizeof(
                    _lib_lvgl.ffi.typeof(self._obj).item
                )

        return _lib_lvgl.ffi.buffer(
            _lib_lvgl.ffi.cast('char *', self._obj),
            size
        )

class _CallbackScalarPointer:
    """MicroPython-compatible wrapper for scalar T * callback arguments."""

    def __init__(self, c_obj, c_type):
        self._obj = c_obj
        self._c_type = c_type

    def __dereference__(self, size=None):
        """Dereference using MicroPython LVGL pointer semantics.

        With no size, return the scalar value.

        With an explicit size, return a writable byte view of the
        pointed-to memory.
        """
        if size is None:
            return _get_py_obj(
                self._obj[0],
                self._c_type,
            )

        return _lib_lvgl.ffi.buffer(
            _lib_lvgl.ffi.cast('char *', self._obj),
            size,
        )

    def __getitem__(self, index):
        return _get_py_obj(
            self._obj[index],
            self._c_type,
        )

    def __setitem__(self, index, value):
        self._obj[index] = _get_c_obj(
            value,
            self._c_type,
        )        
    
def _get_py_callback_ptr(c_obj, c_type):
    if c_obj == _lib_lvgl.ffi.NULL:
        return None

    try:
        ffi_type = _lib_lvgl.ffi.typeof(c_obj)
    except TypeError:
        return _get_py_obj(c_obj, c_type)

    if ffi_type.kind != 'pointer':
        return _get_py_obj(c_obj, c_type)

    # Struct/union pointers retain the normal LVGL wrapper behaviour.
    if ffi_type.item.kind in ('struct', 'union'):
        return _get_py_obj(c_obj, c_type)

    # char * represents a C string.
    if (
        ffi_type.item.kind == 'primitive'
        and ffi_type.item.cname == 'char'
    ):
        return _get_py_obj(c_obj, 'char')

    if ffi_type.item.kind == 'primitive':
        return _CallbackScalarPointer(c_obj, c_type)

    # void * and untyped buffers.
    return _CallbackPointer(c_obj, c_type)


_callback_return_refs = {}

def _get_callback_return(py_obj, c_type, is_pointer):
    if py_obj is None:
        if is_pointer:
            return _lib_lvgl.ffi.NULL
        return None

    if not is_pointer:
        return _get_c_obj(py_obj, c_type)

    # Already wrapped C object/pointer.
    if hasattr(py_obj, '_obj'):
        return py_obj._obj

    # C string returned as pointer.
    if isinstance(py_obj, str):
        data = py_obj.encode('utf-8')
        ref = _lib_lvgl.ffi.new('char[]', data)

        key = id(ref)
        _callback_object_handles[key] = ref
        return ref

    # Raw buffers returned as pointers.
    if isinstance(py_obj, (bytearray, memoryview)):
        ref = _lib_lvgl.ffi.from_buffer(py_obj)

        key = id(ref)
        _callback_object_handles[key] = (py_obj, ref)
        return ref

    if isinstance(py_obj, bytes):
        ref = _lib_lvgl.ffi.new('char[]', py_obj)

        key = id(ref)
        _callback_object_handles[key] = ref
        return ref

    # MicroPython binding permits arbitrary Python objects to cross a
    # void * callback boundary.  Represent those with a CFFI handle.
    if c_type in ('void', 'Any', 'None'):
        return _make_callback_object_handle(py_obj)

    return _get_c_obj(py_obj, c_type)
    

class _AsArrayMixin:
    _c_type = ''

    @classmethod
    def as_array(cls, size=None):
        new_cls = type(
            cls.__name__ + ('[]' if size is None else f'[{size}]'),
            (_Array,),
            {'_c_type': cls._c_type.split(' ')[0]}
        )

        return new_cls()


class _Array(list):
    _c_type = ''

    def as_buffer(self, c_type, size=None):
        if size is None:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[]', self._obj)
        else:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[{size}]', self._obj)
        return _lib_lvgl.ffi.buffer(cast)[:]

    @property
    def _obj(self):
        if self.__obj is None:
            c_array = []
            dim = self._dim

            for item in self._array:
                # Pointer arrays need different treatment from arrays of
                # scalar/struct values. In particular LVGL APIs such as
                # lv_keyboard_set_map() take `const char * const map[]`.
                if '*' in self._c_type:
                    if item is None:
                        c_array.append(_lib_lvgl.ffi.NULL)

                    elif (
                        self._c_type.replace('const', '').strip() == 'char *'
                        and isinstance(item, (str, bytes, bytearray))
                    ):
                        if isinstance(item, str):
                            item = item.encode('utf-8')
                        else:
                            item = bytes(item)

                        # ffi.new("char[]", bytes) adds terminating NUL.
                        ref = _lib_lvgl.ffi.new('char[]', item)
                        self.__refs.append(ref)
                        c_array.append(ref)

                    else:
                        c_array.append(_get_c_obj(item, self._c_type))

                else:
                    c_obj = _get_c_obj(item, self._c_type)
                    py_obj = _get_py_obj(c_obj, self._c_type)

                    if hasattr(py_obj, 'as_dict'):
                        c_array.append(py_obj.as_dict())
                    else:
                        # Scalar C array element.
                        c_array.append(c_obj)

                if isinstance(item, _Array):
                    dim += item._dim

            if '[' in self.__class__.__name__:
                size = self.__class__.__name__.split('[')[-1]
                size = size.split(']')[0]

                if not size:
                    size = str(len(c_array))

                if size and size.isdigit():
                    dim = dim.split(']', 1)[-1]

                    dim = '[{0}]'.format(size) + dim

                    if c_array:
                        try:
                            self.__obj = _lib_lvgl.ffi.new(
                                self._c_type + dim,
                                c_array
                            )
                        except _lib_lvgl.ffi.error:
                            self.__obj = _lib_lvgl.ffi.new(
                                f'lv_{self._c_type}{dim}',
                                c_array
                            )
                    else:
                        self.__obj = _lib_lvgl.ffi.new(
                            self._c_type + dim
                        )
                    return self.__obj

            c_type = self._c_type + dim

            try:
                self.__obj = _lib_lvgl.ffi.new(
                    c_type,
                    [c_array]
                )
            except _lib_lvgl.ffi.error:
                self.__obj = _lib_lvgl.ffi.new(f'lv_{c_type}', [c_array])

        return self.__obj

    @_obj.setter
    def _obj(self, c_obj):
        size = _lib_lvgl.ffi.typeof(c_obj).length
        array = []

        dim = ''

        for i in range(size):
            c_item = c_obj[i]
            py_item = _get_py_obj(c_item, self._c_type)

            if py_item is None:
                break

            if isinstance(py_item, _Array) and not dim:
                dim += py_item._dim

            array.append(py_item)

        self.__class__.__name__ = '{0}[{1}]{2}'.format(self._c_type, size, dim)

        self._array = array
        self.__obj = c_obj

    @property
    def _dim(self):
        size = len(self)
        return '[]' if size == 0 else '[{0}]'.format(size)

    def __init__(self):
        self.__obj = None

        # Keep backing allocations for pointer-array elements alive for as
        # long as the C array exists (e.g. char[] strings referenced by
        # char *[]).
        self.__refs = []

        self._array = []
        list.__init__(self)

    def __len__(self):
        return len(self._array)

    def __iter__(self):
        return iter(self._array)

    def __getitem__(self, item):
        return self._array[item]

    def __setitem__(self, key, value):
        self.__check_locked()

        self._array[key] = value

    @property
    def is_locked(self):
        return self.__obj is not None

    def __check_locked(self):
        if self.__obj is not None:
            raise RuntimeError(
                'This array "{0}" has been recieved from LVGL or '
                'sent to LVGL and has been locked\n'
                'you can make copy using `array.copy()` '
                'to add/change/remove items from the array.'.format(
                    self.__class__.__name__
                )
            )

    def add_dimension(self) -> "_Array":
        self.__check_locked()

        cls = type(f'{self._c_type}[]', (_Array,), {'_c_type': self._c_type})
        instance = cls()
        self._array.append(instance)
        return instance

    def clear(self) -> None:
        self.__check_locked()
        self._array.clear()

    def copy(self) -> "_Array":
        """
        This is a shallow copy
        """
        cls = type(
            self.__class__.__name__,
            (_Array,),
            {'_c_type': self._c_type}
        )

        instance = cls()

        if self.__class__.__name__.count('[') > 1:
            for item in self._array:
                instance.append(item.copy())

        else:
            instance._array = list(self)[:]

        return instance

    def pop(self, index: int = 0) -> Any:
        self.__check_locked()

        return self._array.pop(index)

    def index(
            self,
            value: Any,
            start: Optional[int] = None,
            stop: Optional[int] = None
    ) -> int:
        if None not in (start, stop):
            return self._array.index(value, start, stop)

        if start is not None:
            return self._array.index(value, start)

        return self._array.index(value)

    def count(self, obj: Any) -> int:
        return self._array.count(obj)

    def insert(self, index: int, obj: Any) -> None:
        self.__check_locked()

        self._array.insert(index, obj)

    def remove(self, value: Any) -> None:
        self.__check_locked()

        self._array.remove(value)

    def reverse(self) -> None:
        self.__check_locked()

        self._array.reverse()

    def sort(
            self,
            *,
            key: Optional[Callable[[Any], Any]] = None,
            reverse: Optional[bool] = False
    ) -> None:
        self.__check_locked()

        if key is not None:
            self._array.sort(key=key, reverse=reverse)

        self._array.sort(reverse=reverse)

    def __delitem__(self, i: Union[int, slice]) -> None:
        self.__check_locked()

        del self._array[i]

    def __add__(self, x: Union["_Array", list]) -> "_Array":
        instance = self.copy()

        for item in x:
            instance.append(item)

        return instance

    def __iadd__(self, x: Union["_Array", list]) -> "_Array":
        self.__check_locked()

        for item in x:
            self.append(item)

        return self

    def __mul__(self, n: int) -> "_Array":
        instance = self.copy()

        instance._array = instance._array * n
        return instance

    def __rmul__(self, n: int) -> "_Array":
        return self.__mul__(n)

    def __imul__(self, n: int) -> "_Array":
        self.__check_locked()
        self._array *= n
        return self

    def __contains__(self, obj: Any) -> bool:
        return obj in self._array

    def __reversed__(self) -> "_Array":
        self.__check_locked()
        self._array.__reversed__()
        return self

    def __gt__(self, x: "_Array") -> bool:
        return self._array > x._array

    def __ge__(self, x: "_Array") -> bool:
        return self._array >= x._array

    def __lt__(self, x: "_Array") -> bool:
        return self._array < x._array

    def __le__(self, x: "_Array") -> bool:
        return self._array <= x._array

    def __eq__(self, other: "_Array") -> bool:
        return self._array == other._array

    def __ne__(self, other: "_Array") -> bool:
        return not self.__eq__(other)

    def extend(self, obj: Union[list, "_Array"]) -> None:
        self.__check_locked()

        for item in obj:
            self.append(item)

    def append(self, py_obj: Any) -> None:
        self.__check_locked()

        if isinstance(py_obj, tuple):
            py_obj = list(py_obj)

        if isinstance(py_obj, list) and not isinstance(py_obj, _Array):
            if self._array and not isinstance(self._array[0], _Array):
                raise TypeError(
                    'You cannot add an array to a single dimension array.'
                )

            dim = self.add_dimension()
            for item in py_obj:
                if isinstance(item, _Array) and item.is_locked:
                    item = item.copy()

                dim.append(item)

            return
        try:
            if self._c_type in (
            py_obj._c_type, py_obj.__class__.__name__):  # NOQA
                self._array.append(py_obj)
                return

        except AttributeError:
            # Pointer arrays retain Python values until `_obj` is
            # materialized. `_obj` then converts None to NULL, strings to
            # stable char[] allocations, and wrappers to C pointers.
            if '*' in self._c_type:
                self._array.append(py_obj)
                return

            if isinstance(py_obj, (int, str, float, bytes, bool)):
                py_type = _convert_basic_type(py_obj, self._c_type)
                self._array.append(py_type)

    def as_dict(self):
        return [item.as_dict() for item in self]

    def __str__(self):
        return str(self._array)

    def __repr__(self):
        return repr(self._array)


def _convert_basic_type(obj, c_type):
    try:
        if c_type in (obj._c_type, obj.__class__.__name__):  # NOQA
            return obj
        else:
            raise TypeError('incompatable type')
    except AttributeError:
        pass

    glob = globals()

    def _instance(_c_type):
        c = glob[_c_type]
        c = type(
            c_type,
            (c,),
            {'_obj': obj, '_c_type': f'{c_type} *'}
        )

        try:
            return c()
        except Exception:  # NOQA
            ins = c()
            ins._obj = obj
            return ins

    if c_type in glob:
        return _instance(c_type)

    if f'{c_type}_' in glob:
        return _instance(f'{c_type}_')

    if isinstance(obj, bool):
        if c_type != 'bool':
            raise TypeError(
                f'incompatible types "bool" and "{c_type}"'
            )

        cls = type(
            c_type,
            (_Bool,),
            {'_obj': obj, '_c_type': f'{c_type} *'}
        )
        return cls(obj)

    if isinstance(obj, float):
        for item in ('double', 'float'):
            if c_type.startswith(item):
                cls = type(
                    c_type,
                    (_Float,),
                    {'_obj': obj, '_c_type': f'{c_type} *'}
                )
                return cls(obj)

        raise TypeError(
            f'incompatible types "float" and "{c_type}"'
        )

    if isinstance(obj, bytes) and c_type == 'char':
        obj = obj.decode('utf-8')

    if isinstance(obj, str):
        if c_type != 'char':
            raise TypeError(
                f'incompatible types "str" and "{c_type}"'
            )

        cls = type(
            c_type,
            (_String,),
            {'_obj': obj, '_c_type': f'{c_type} *'}
        )

        return cls(obj)

    raise TypeError(f'Unknown type ("{c_type}")')


class _Float(float, _AsArrayMixin):
    _c_type = 'float *'
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance


class _Integer(int, _AsArrayMixin):
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance


class _String(str, _AsArrayMixin):
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value.encode('utf-8')
        return instance


class _Bool(int, _AsArrayMixin):
    _c_type = 'bool *'
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance


class void(_AsArrayMixin):
    _c_type = 'void *'

    def as_dict(self):
        return self._obj

    def __init__(self, value):
        try:
            self._obj = _lib_lvgl.ffi.cast(self._c_type, value)
            self.ctype = _get_c_type(value)

        except Exception:  # NOQA
            c_obj = _get_c_obj(value, None)

            try:
                self._obj = _lib_lvgl.ffi.cast(self._c_type, c_obj)
                self.ctype = _get_c_type(c_obj)
                value = c_obj
            except Exception:  # NOQA
                self._obj = value

        self.__original__object__ = value

    def __str__(self):
        return f'(void *) ({self.ctype})'


class char(_String):
    _c_type = 'char *'


class uint8_t(_Integer):
    _c_type = 'uint8_t *'

    @classmethod
    def from_buffer(cls, data):
        return _lib_lvgl.ffi.from_buffer(cls._c_type.split(' ')[0] + '[]', data)

class uint16_t(_Integer):
    _c_type = 'uint16_t *'


class uint32_t(_Integer):
    _c_type = 'uint32_t *'


class uint64_t(_Integer):
    _c_type = 'uint64_t *'


class int8_t(_Integer):
    _c_type = 'int8_t *'


class int16_t(_Integer):
    _c_type = 'int16_t *'


class int32_t(_Integer):
    _c_type = 'int32_t *'


class int64_t(_Integer):
    _c_type = 'int64_t *'


class int_(_Integer):
    _c_type = 'int *'


class uintptr_t(_Integer):
    _c_type = 'unsigned int *'


class intptr_t(_Integer):
    _c_type = 'signed int *'


class size_t(_Integer):
    _c_type = 'size_t *'



# This class checks to see if wrapper classes are being used by
# the mpy module. The reason why this meta class exists is so that objects
# comming from C code get redirected to those wrapper classes instead of to
# the C API classes. If the redirection does not occur then the methods in
# the wrapper classes would not be accessible.
class _StructUnionMeta(type):
    _wrapped_classes = {}
    _classes = {}
    _calling_from_meta = False

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        # Only classes generated in lvgl.mpy are wrappers.
        # Raw classes now live in lvgl._raw.
        if cls.__module__.endswith('.mpy'):
            _StructUnionMeta._wrapped_classes.setdefault(name, cls)

    @staticmethod
    def get_wrapper(cls):
        name = cls.__name__

        if cls.__module__.endswith('mpy'):
            return cls

        wrapped = _StructUnionMeta._wrapped_classes

        if name.endswith('_t') and name[:-2] in wrapped:
            return wrapped[name[:-2]]

        if name.startswith('_') and name[1:] in wrapped:
            return wrapped[name[1:]]

        if name in wrapped:
            return wrapped[name]

        return cls

    def __call__(cls, *args, **kwargs):
        # MicroPython LVGL struct syntax:
        #
        #     lv.image_dsc_t({
        #         "data_size": 123,
        #         "data": buffer,
        #     })
        #
        if len(args) == 1 and isinstance(args[0], dict):
            if kwargs:
                raise TypeError(
                    "cannot combine dict initializer with keyword arguments"
                )

            kwargs = dict(args[0])
            args = ()

        if not _StructUnionMeta._calling_from_meta:
            cls = _StructUnionMeta.get_wrapper(cls)

        _StructUnionMeta._calling_from_meta = True

        try:
            return super(_StructUnionMeta, cls).__call__(
                *args,
                **kwargs,
            )
        finally:
            _StructUnionMeta._calling_from_meta = False


class _StructUnion(_AsArrayMixin, metaclass=_StructUnionMeta):
    _c_type = ''

    @classmethod
    def sizeof(cls):
        return _lib_lvgl.ffi.sizeof(cls._c_type)

    def cast(self, obj):
        obj._obj = self._obj

    def as_buffer(self, c_type, size=None):
        if size is None:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[]', self._obj)
        else:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[{size}]', self._obj)
        return _lib_lvgl.ffi.buffer(cast)[:]

    def __init__(self, **kwargs):
        self._obj = _lib_lvgl.ffi.new(self._c_type)

        for key, value in list(kwargs.items())[:]:
            if value == _DefaultArg:
                continue

            attr = getattr(self._obj, key)
            c_type = _get_c_type(attr)
            self._set_field(key, value, c_type)

    def _get_field(self, field_name, c_type):
        key = '__py_{0}__'.format(field_name)
        if key in self.__dict__:
            obj = self.__dict__[key]
            if isinstance(obj, (_StructUnion, _Array)):
                return obj

        py_obj = _get_py_obj(getattr(self._obj, field_name), c_type)

        self.__dict__[key] = py_obj
        return py_obj

    def _set_field(self, field_name, py_obj, c_type):
        def _setattr():
            setattr(self._obj, field_name, c_obj)
            self.__dict__['__py_{0}__'.format(field_name)] = py_obj
            self.__dict__['__c_{0}__'.format(field_name)] = c_obj

        if isinstance(py_obj, list):
            c_obj = [item.as_dict() for item in py_obj]
            _setattr()
            return

        # The generated Python type can lose pointer information, so inspect
        # the destination field's real CFFI type.
        try:
            field_type = _lib_lvgl.ffi.typeof(
                getattr(self._obj, field_name)
            )
        except (AttributeError, TypeError):
            field_type = None

        # Python str -> retained NUL-terminated storage for string pointers.
        if (
            isinstance(py_obj, str)
            and field_type is not None
            and field_type.kind == 'pointer'
            and (
                field_type.item.kind == 'void'
                or (
                    field_type.item.kind == 'primitive'
                    and field_type.item.cname == 'char'
                )
            )
        ):
            c_obj = _lib_lvgl.ffi.new(
                'char[]',
                py_obj.encode('utf-8'),
            )

            _setattr()
            return

        # bytes/bytearray/memoryview -> primitive C pointer.
        #
        # This covers e.g. lv_image_dsc_t.data, whose generated Python type
        # can say "uint8_t" even though the real field is uint8_t *.
        if (
            isinstance(py_obj, (bytes, bytearray, memoryview))
            and field_type is not None
            and field_type.kind == 'pointer'
            and field_type.item.kind == 'primitive'
        ):
            if isinstance(py_obj, bytes):
                backing = bytearray(py_obj)
            elif isinstance(py_obj, memoryview) and py_obj.readonly:
                backing = bytearray(py_obj)
            else:
                backing = py_obj

            try:
                buffer_obj = _lib_lvgl.ffi.from_buffer(backing)
            except (TypeError, BufferError):
                backing = bytearray(py_obj)
                buffer_obj = _lib_lvgl.ffi.from_buffer(backing)

            c_obj = _lib_lvgl.ffi.cast(
                field_type.cname,
                buffer_obj,
            )

            # Keep both the Python buffer and CFFI view alive.
            self.__dict__[
                '__buffer_{0}__'.format(field_name)
            ] = backing

            _setattr()
            return

        c_obj = _get_c_obj(py_obj, c_type)

        # Struct wrappers own T *, whereas embedded struct fields require T.
        try:
            src_type = _lib_lvgl.ffi.typeof(c_obj)

            if (
                field_type is not None
                and field_type.kind in ('struct', 'union')
                and src_type.kind == 'pointer'
                and src_type.item.kind in ('struct', 'union')
            ):
                c_obj = c_obj[0]

        except TypeError:
            pass

        _setattr()


    def as_dict(self):
        res = {}
        for field in dir(self._obj):
            attr = getattr(self, field)
            res[field] = attr.as_dict()

        return res

_PY_C_TYPES = (_Float, _Integer, _String, _StructUnion)
_global_cb_store = _CBStore()
_global_cb_handles = set()
