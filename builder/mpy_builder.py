import sys
import os
import inspect

from .binding_model import BindingModel, parse_symbols
from .raw_api_model import RawClass, RawFunction, parse_raw_api


_GENERATOR_INTERNAL_NAMES = {
    '_StructUnion',
    '_String',
    '_Bool',
    '_CBStore',
    '_lib_lvgl',
    '_get_c_obj',
    '_get_py_obj',
    '_get_c_type',
    '_Array',
    '_AsArrayMixin',
    '_DefaultArg',
    '_Integer',
    '_PY_C_TYPES',
    'Union',
    'Any',
    'Callable',
    'Optional',
    'List',
    '_Float',
    '_convert_basic_type',
}


def _find_symbol_header(lib_path):
    relative_path = os.path.join(
        'src',
        'lvgl',
        'src',
        'font',
        'lv_symbol_def.h'
    )
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    candidates = (
        os.path.join(lib_path, relative_path),
        os.path.join(project_path, relative_path),
    )
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    raise FileNotFoundError(
        'Unable to locate lv_symbol_def.h; checked: '
        + ', '.join(candidates)
    )


def run(lib_path, model: BindingModel | None = None):
    lvgl_path = os.path.join(lib_path, 'lvgl')
    raw_api = parse_raw_api(os.path.join(lvgl_path, '_raw.py'))

    symbol_header = _find_symbol_header(lib_path)

    model_symbols = model.symbols if model is not None and model.symbols else (
        parse_symbols(symbol_header)
    )
    symbols = tuple((symbol.name, symbol.value) for symbol in model_symbols)

    functions = {}
    structs_unions = {}
    enum_items = {}

    create_funcs = {}
    other = []

    basic_types = []

    for key, value in raw_api.items():
        if key == '_MPY_API':
            continue

        if key in _GENERATOR_INTERNAL_NAMES:
            continue

        if key.startswith('__'):
            continue

        if isinstance(value, RawFunction):
            if (
                key.endswith('_create')
                and not key.startswith('sdl')
                and not key.startswith('indev')
            ):
                create_funcs[key] = value
            else:
                functions[key] = value

        elif key.isupper():
            enum_items[key] = key

        else:
            if isinstance(value, RawClass):
                if raw_api.class_is_subclass(value, '_StructUnion'):
                    structs_unions[key] = {
                        'cls': value,
                        'name': key,
                        'p_methods': {},
                        'methods': {},
                        'enums': {}
                    }
                elif any(
                    raw_api.class_is_subclass(value, base_name)
                    for base_name in (
                        '_Float',
                        '_Integer',
                        '_String',
                        '_Bool',
                        'void',
                    )
                ):
                    basic_types.append(key)
            else:
                other.append(key)

    obj_classes = {}

    def convert_type(ano):
        if ano == 'void':
            return '_lvgl.void'


        for type_ in basic_types:
            if type_ in ano:
                return ano

        if '_Bool' in ano:
            if '_lvgl' not in ano:
                ano = ano.replace('_Bool', '_lvgl._Bool')
            return ano

        if 'List[' in ano:
            ano = ano.split('List[')[1:]
            for i, itm in enumerate(ano):
                if '_lvgl' in itm:
                    itm = itm.replace('_lvgl.', '"')[:-1] + '"]'
                    ano[i] = itm
            ano.insert(0, '')
            ano = 'List['.join(ano)
            ano = ano.replace('obj_t', 'obj')
            return ano

        if '_lvgl' in ano:
            ano = ano.replace('_lvgl.', '"') + '"'

        ano = ano.replace('obj_t', 'obj')

        return ano

    def convert_annotation(annot):
        try:
            annot = annot.__name__
        except:  # NOQA
            annot = str(annot)

        annot = annot.replace("ForwardRef('", '').replace("')", '')

        if annot.startswith('typing'):
            annot = annot.replace('typing.', '')
            if annot.startswith('List['):
                annot = annot.split('List[')[1:]

                for i, itm in enumerate(annot):
                    if itm.startswith('typing'):
                        itm = itm.replace('typing.', '')
                    else:
                        itm = itm.lstrip('_')
                        itm = f'_lvgl.{itm}'
                    annot[i] = itm

                annot.insert(0, '')
                annot = 'List['.join(annot)
                return annot

            return annot

        if '"' in annot:
            qoted = True
            annot = annot.replace('"', '')
        else:
            qoted = False

        annot = annot.replace('bool', '_Bool')

        if not annot.startswith('_Bool'):
            annot = annot.lstrip('_')

        if annot.startswith('List['):
            annot.replace('List[', '')
            if annot.startswith('typing'):
                annot = annot.replace('typing.', '')
                return f'List[{annot}'

            if not annot.startswith('_Bool'):
                annot = annot.lstrip('_')
            annot = f'List[_lvgl.{annot}'
        elif qoted:
            if not annot.startswith('_Bool'):
                annot = annot.lstrip('_')
            annot = f'_lvgl.{annot}'

        elif annot != 'None':
            if not annot.startswith('_Bool'):
                annot = annot.lstrip('_')
            annot = f'_lvgl.{annot}'

        return annot

    for name, func in create_funcs.items():
        cls_name = name.replace('_create', '')

        sig = func.signature
        params = list(sig.parameters.items())

        if not params:
            functions[name] = func
            continue

        param_name, param = params[0]
        notation = param.annotation

        if notation == param.empty:
            functions[name] = func
            continue

        p_notation = convert_annotation(notation).replace('_lvgl.', '')
        ret_val = convert_annotation(sig.return_annotation).replace('_lvgl.', '')

        if ret_val != p_notation:
            functions[name] = func
            continue

        new_params = ['self']
        param_names = []

        for index, (p_name, param) in enumerate(params):
            if param.kind == param.VAR_POSITIONAL:
                p_name = f'*{p_name}'
                new_params.append(p_name)
            else:
                anno = convert_annotation(param.annotation)

                # MicroPython LVGL widget constructors allow parent to be omitted.
                # A NULL parent creates a screen/root widget.
                if index == 0 and p_name == 'parent':
                    new_params.append(f'{p_name}: {anno} = None')
                else:
                    new_params.append(f'{p_name}: {anno}')

            param_names.append(p_name)

        obj_classes[cls_name] = {
            'name': cls_name,
            'methods': {},
            'enums': {},
            'create_func_name': name,
            'parent_cls': p_notation,
            'arg_names': ', '.join(param_names),
            'args': ', '.join(new_params),
            'type': ret_val
        }


    def get_common_name(name1, name2, limit=99):
        name1 = name1.split('_')
        name2 = name2.split('_')

        res = []

        for i in range(min(len(name1), len(name2))):
            if len(res) == limit:
                break

            if name1[i] != name2[i]:
                break

            res.append(name1[i])

        return '_'.join(res)


    def get_uncommon_name(name1, name2):
        cmmon = get_common_name(name1, name2)
        cmmon += '_'

        return name2.replace(cmmon, '', 1)


    for cls_name1, cls in obj_classes.items():
        cls_name2 = cls['parent_cls']
        matched_name = ''

        for cls_name3 in obj_classes.keys():
            if cls_name1 == cls_name3:
                continue

            common_name = get_common_name(cls_name2, cls_name3)

            if not common_name:
                continue

            if len(common_name) > len(matched_name):
                matched_name = cls_name3

        if not matched_name:
            # Some factory names (for example ``draw_layer``) do not share a
            # prefix with the C return type.  In that case the generated LVGL
            # wrapper is still the correct base class.
            cls['parent_cls'] = f'_lvgl.{cls_name2}'
            continue

        cls['parent_cls'] = matched_name


    for func_name, func in list(functions.items()):
        # Animation path functions are callbacks, not anim instance methods.
        # MicroPython LVGL exposes them at module level, e.g.
        #
        #     anim.set_path_cb(lv.anim_path_ease_in)
        #
        if func_name.startswith('anim_path_'):
            continue

        match = None
        matched_common_name = ''
        for cls_name, cont in obj_classes.items():

            # Only treat a function as a method when its C/Python name actually
            # belongs to that class. A partial common prefix is not sufficient:
            #
            #   draw_rect     != draw_layer.*
            #   draw_image    != draw_layer.*
            #
            # The old get_common_name() heuristic incorrectly consumed these
            # module-level drawing functions.
            if not func_name.startswith(cls_name + '_'):
                continue

            common = cls_name

            sig = func.signature
            
            params = list(sig.parameters.items())
            if not params:
                continue

            param_name, param = params[0]

            anno = param.annotation
            if anno == param.empty:
                continue

            anno = convert_annotation(anno).replace('_lvgl.', '')

            if cont['type'] != anno:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        if match is None:
            continue

        del functions[func_name]

        new_params = ['self']
        param_names = ['self']

        sig = func.signature

        for param_name, param in list(sig.parameters.items())[1:]:
            if param.kind == param.VAR_POSITIONAL:
                param_name = f'*{param_name}'
                new_params.append(param_name)
            else:
                anno = convert_annotation(param.annotation)
                anno = anno.replace('NoneType', 'void')
                anno = convert_type(anno)
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        raw_return_annotation = convert_annotation(sig.return_annotation)
        returns_obj = (
            raw_return_annotation
            .replace('_lvgl.', '')
            .strip('"')
            == 'obj_t'
        )

        anno = convert_type(raw_return_annotation)
        ret_val = f' -> {anno}'

        new_func_name = get_uncommon_name(match['name'], func_name)
        if new_func_name == 'del':
            new_func_name = '_del'
        match['methods'][new_func_name] = {
            'name': func_name,
            'ret_val': ret_val,
            'params': ', '.join(new_params),
            'param_names': ', '.join(param_names),
            'returns_obj': returns_obj,
        }
    structs = {}

    for func_name, func in list(functions.items()):
        if func_name.startswith('anim_path_'):
            continue

        match = None
        matched_common_name = ''

        sig = func.signature
        params = list(sig.parameters.items())
        if not params:
            continue

        param_name, param = params[0]

        anno = param.annotation
        if anno == param.empty:
            continue

        anno = convert_annotation(anno).replace('_lvgl.', '')


        for struct_name, cont in structs.items():
            common = get_common_name(func_name, struct_name)
            if not common:
                continue

            if struct_name != anno:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        for struct_name, cont in structs_unions.items():
            common = get_common_name(func_name, struct_name)
            if not common:
                continue

            if struct_name != anno:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        if match is None:
            continue

        del functions[func_name]

        new_params = ['self']
        param_names = ['self']

        for param_name, param in list(sig.parameters.items())[1:]:
            if param.kind == param.VAR_POSITIONAL:
                param_name = f'*{param_name}'
                new_params.append(param_name)
            else:
                anno = convert_annotation(param.annotation)
                anno = anno.replace('NoneType', 'void').replace('None', 'void')
                anno = convert_type(anno)
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        raw_return_annotation = convert_annotation(sig.return_annotation)
        returns_obj = (
            raw_return_annotation
            .replace('_lvgl.', '')
            .strip('"')
            == 'obj_t'
        )

        anno = convert_type(raw_return_annotation)
        ret_val = f' -> {anno}'

        new_func_name = get_uncommon_name(match['name'], func_name)
        if new_func_name == 'del':
            new_func_name = '_del'

        match['methods'][new_func_name] = {
            'name': func_name,
            'ret_val': ret_val,
            'params': ', '.join(new_params),
            'param_names': ', '.join(param_names),
            'returns_obj': returns_obj,
        }

        structs[match['name']] = match
        try:
            del structs_unions[match['name']]
        except KeyError:
            pass

    # Tuples keep generated output stable across Python hash seeds.
    flat_constants = (
        'RADIUS_CIRCLE',
        'IMAGE_HEADER_MAGIC',
    )
    flat_constant_aliases = (
        'GRID_CONTENT',
        'GRID_TEMPLATE_LAST',
    )

    for enum_name, val in sorted(list(enum_items.items())):
        # These must remain module-level MicroPython-compatible constants.
        # Do not associate them with widget classes.
        if enum_name in flat_constants:
            continue

        match = None
        matched_common_name = ''

        for cls_name, cont in obj_classes.items():
            common = get_common_name(enum_name.lower(), cls_name, 2)

            if not common:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        if match is None:
            continue

        new_enum_name = enum_name.replace(
            matched_common_name.upper() + '_',
            ''
        )
        match['enums'][new_enum_name] = enum_name
        del enum_items[enum_name]


    for cls_name, cont in obj_classes.items():

        def _match_enums(mtched_name=None):
            if mtched_name is not None:
                matches = []

                for enum, vl in list(cont['enums'].items()):
                    comm = get_common_name(mtched_name, enum, 3)

                    if not comm:
                        continue

                    if comm != mtched_name:
                        continue

                    matches.append((enum, vl))

                m_enums = {}
                matched_enums = {}

                for mtch, vl in matches:
                    del cont['enums'][mtch]
                    n_enum_name = get_uncommon_name(mtched_name, mtch)
                    m_enums[n_enum_name] = [mtch, vl]

                matched_enums[mtched_name] = m_enums

                return matched_enums

            matched_enums = {}

            for enum1, val1 in list(cont['enums'].items()):
                matches = []
                mtched_name = ''

                for enum2, val2 in list(cont['enums'].items()):
                    if enum1 == enum2:
                        continue

                    comm = get_common_name(enum1, enum2, 2)
                    if not comm:
                        continue

                    if len(comm) > len(mtched_name):
                        mtched_name = comm
                        matches = [(enum1, val1)]

                    matches.append((enum2, val2))

                if mtched_name:
                    m_enums = {}

                    for mtch, vl in matches:
                        del cont['enums'][mtch]
                        n_enum_name = get_uncommon_name(mtched_name, mtch)
                        m_enums[n_enum_name] = [mtch, vl]

                    matched_enums[mtched_name] = m_enums

            return matched_enums

        storage = {}
        if cls_name == 'obj':
            storage.update(_match_enums('CLASS_THEME_INHERITABLE'))
            storage.update(_match_enums('CLASS_GROUP_DEF'))
            storage.update(_match_enums('CLASS_EDITABLE'))

        elif cls_name == 'chart':
            storage.update(_match_enums('AXIS_PRIMARY'))
            storage.update(_match_enums('AXIS_SECONDARY'))

        elif cls_name == 'imgbtn':
            storage.update(_match_enums('STATE'))

        elif cls_name == 'menu':
            storage.update(_match_enums('ROOT_BACK_BTN'))


        storage.update(_match_enums())
        cont['enums'] = storage

    used = []

    output = open(os.path.join(lvgl_path, 'mpy.py'), 'w')
    output.write('from typing import Union, Any, Callable, Optional, List  # NOQA\n')
    output.write('import importlib as _importlib\n\n')
    output.write('_lvgl = _importlib.import_module(__package__ + "._raw")\n')
    output.write('_MPY_API = True\n\n\n')
    output.write(
        '_retained_obj_refs = {}\n'
        '\n'
        'def _obj_ref_key(obj):\n'
        '    ptr = _lvgl._lib_lvgl.ffi.cast("uintptr_t", obj._obj)\n'
        '    return int(ptr)\n'
        '\n'
        'def _retain_obj_ref(obj, slot, value, append=False):\n'
        '    refs = _retained_obj_refs.setdefault(_obj_ref_key(obj), {})\n'
        '    if append:\n'
        '        values = refs.setdefault(slot, [])\n'
        '        if not any(item is value for item in values):\n'
        '            values.append(value)\n'
        '    else:\n'
        '        refs[slot] = value\n'
        '\n'
        'def _release_obj_refs(obj, slot=None):\n'
        '    key = _obj_ref_key(obj)\n'
        '    if slot is None:\n'
        '        _retained_obj_refs.pop(key, None)\n'
        '        return\n'
        '    refs = _retained_obj_refs.get(key)\n'
        '    if refs is None:\n'
        '        return\n'
        '    refs.pop(slot, None)\n'
        '    if not refs:\n'
        '        _retained_obj_refs.pop(key, None)\n'
        '\n'
        'def _callback_ref_from_user_data(user_data):\n'
        '    if user_data is None or not hasattr(user_data, "_obj"):\n'
        '        return None\n'
        '    ffi = _lvgl._lib_lvgl.ffi\n'
        '    pointer = int(ffi.cast("uintptr_t", user_data._obj))\n'
        '    for ref, store in _lvgl._global_cb_store.items():\n'
        '        if not isinstance(store, _lvgl._CBStore):\n'
        '            continue\n'
        '        handle = store.get("__handle__")\n'
        '        if handle is None:\n'
        '            continue\n'
        '        if int(ffi.cast("uintptr_t", handle)) == pointer:\n'
        '            return ref\n'
        '    return None\n'
        '\n'
        'def _event_callback_ref(dsc):\n'
        '    return _callback_ref_from_user_data(\n'
        '        _lvgl.event_dsc_get_user_data(dsc)\n'
        '    )\n'
        '\n'
        'def _release_event_callback_ref(ref):\n'
        '    if ref is not None:\n'
        '        _lvgl._global_cb_store.pop(ref, None)\n'
        '\n'
        'def _collect_obj_release_refs(obj):\n'
        '    refs = [(_obj_ref_key(obj), [])]\n'
        '    event_refs = refs[0][1]\n'
        '    for index in range(_lvgl.obj_get_event_count(obj)):\n'
        '        dsc = _lvgl.obj_get_event_dsc(obj, index)\n'
        '        event_refs.append(_event_callback_ref(dsc))\n'
        '    for index in range(_lvgl.obj_get_child_count(obj)):\n'
        '        child = _lvgl.obj_get_child(obj, index)\n'
        '        refs.extend(_collect_obj_release_refs(child))\n'
        '    return refs\n'
        '\n'
        'def _release_collected_obj_refs(refs):\n'
        '    for obj_key, event_refs in refs:\n'
        '        _retained_obj_refs.pop(obj_key, None)\n'
        '        for ref in event_refs:\n'
        '            _release_event_callback_ref(ref)\n'
        '\n\n'
    )
    output.write('class SYMBOL:\n')

    for name, value in symbols:
        output.write(f'    {name} = {value!r}\n')

    output.write('\n\n')

    enum_template = '''
class {name}:
{items}'''

    enum_item_template = '    {name} = _lvgl.{o_name}'

    def output_enum(nme, items, force_class=False):
        new_items = []

        if len(items) == 1 and not force_class:
            output.write(
                '{0} = _lvgl.{1}\n\n'.format(*items[0])
            )
        else:
            for ename, o_name in items:
                if ename[0].isdigit():
                    ename = f'_{ename}'

                new_items.append(
                    f'    {ename} = _lvgl.{o_name}'
                )

            tmpl = enum_template.format(
                name=nme,
                items='\n'.join(new_items) or '    pass'
            )

            output.write(tmpl + '\n\n')

    def sort_enums(mtch_name=None):

        if mtch_name is not None:
            m_enums = []

            for ename, vlue in list(enum_items.items()):

                comm = get_common_name(ename, mtch_name)

                if comm and comm == mtch_name:
                    nenum_name = ename.replace(mtch_name + '_', '')
                    m_enums.append((nenum_name, vlue))
                    used.append(ename)

                    try:
                        del enum_items[ename]
                    except KeyError:
                        continue

            output_enum(mtch_name, m_enums, force_class=True)
            return


        for enum_name1, value1 in list(enum_items.items()):
            if enum_name1 in used:
                continue

            mtched_common_name = ''
            matches = []

            for enum_name2, value2 in list(enum_items.items()):
                if enum_name2 in used:
                    continue

                if enum_name1 == enum_name2:
                    continue

                cmm = get_common_name(enum_name1, enum_name2, 2)

                if not cmm:
                    continue

                if len(cmm) > len(mtched_common_name):
                    matches = [(enum_name1, value1)]
                    mtched_common_name = cmm

                matches.append((enum_name2, value2))

            if not mtched_common_name:
                used.append(enum_name1)
                try:
                    del enum_items[enum_name1]
                except KeyError:
                    pass

                output_enum(enum_name1, [(enum_name1, value1)])
            else:
                m_enums = []

                for ename, vl in matches:
                    try:
                        del enum_items[ename]
                    except KeyError:
                        continue

                    used.append(ename)

                    nenum_name = get_uncommon_name(mtched_common_name, ename)
                    m_enums.append((nenum_name, vl))

                output_enum(mtched_common_name, m_enums[:])

            try:
                del enum_items[enum_name1]
            except KeyError:
                pass

    for const_name in flat_constants:
        if const_name not in enum_items:
            continue

        output.write(
            f'{const_name} = _lvgl.{const_name}\n\n'
        )
        used.append(const_name)
        del enum_items[const_name]

    for const_name in flat_constant_aliases:
        output.write(
            f'{const_name} = _lvgl.{const_name}\n\n'
        )

    for e_name in (
        'EXPLORER',
        'INDEV_TYPE',
        'INDEV_STATE',
        'DRAW_MASK',
        'DRAW_LAYER',
        'FS_RES',
        'FS_MODE',
        'FS_SEEK',
        'DISP_ROTATION',
        'FONT_SUBPX',
        'ANIM_IMG',
        'SPAN_MODE',
        'SPAN_OVERFLOW',
        'FLEX_ALIGN',
        'FLEX_FLOW',
        'GRID_ALIGN',
        'GRID',
        'COLOR_FORMAT',
        'STYLE_RES',
        'STYLE_PROP',
        'SCREEN_LOAD_ANIM',
        'TEXT_ALIGN',
    ):
        sort_enums(e_name)

    '''
    OBJ_CLASS_EDITABLE
    OBJ_CLASS_GROUP
    OBJ_CLASS_THEME

    CHART_AXIS

    IMGBTN_STATE
    MENU_ROOT
    '''
    sort_enums()

    class_template = '''\
class {name}({parent_cls}):
{enums}
    def __init__({args}):
        for arg in ({arg_names},):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.{create_func_name}({arg_names})
            cls.cast(self)

{identity_methods}
{methods}'''

    obj_identity_methods = '''\
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
'''

    method_template = '''\
    def {name}({args}){ret_val}:
        return _lvgl.{o_name}({arg_names})
'''

    obj_method_template = '''\
    def {name}({args}){ret_val}:
        return _wrap_obj(_lvgl.{o_name}({arg_names}))
'''

    retained_ref_method_template = '''\
    def {name}({args}){ret_val}:
        _retain_obj_ref(self, '{slot}', {ref_arg}{append_arg})
        return _lvgl.{o_name}({arg_names})
'''

    release_ref_method_template = '''\
    def {name}({args}){ret_val}:
        result = _lvgl.{o_name}({arg_names})
        _release_obj_refs(self, '{slot}')
        return result
'''

    remove_event_method_template = '''\
    def {name}({args}){ret_val}:
        dsc = _lvgl.obj_get_event_dsc(self, index)
        callback_ref = _event_callback_ref(dsc)
        result = _lvgl.{o_name}({arg_names})
        if result:
            _release_event_callback_ref(callback_ref)
        return result
'''

    remove_event_dsc_method_template = '''\
    def {name}({args}){ret_val}:
        callback_ref = _event_callback_ref(dsc)
        result = _lvgl.{o_name}({arg_names})
        if result:
            _release_event_callback_ref(callback_ref)
        return result
'''

    delete_obj_method_template = '''\
    def {name}({args}){ret_val}:
        refs = _collect_obj_release_refs(self)
        result = _lvgl.{o_name}({arg_names})
        _release_collected_obj_refs(refs)
        return result
'''

    delete_timer_method_template = '''\
    def {name}({args}){ret_val}:
        callback_ref = _callback_ref_from_user_data(
            _lvgl.timer_get_user_data(self)
        )
        result = _lvgl.{o_name}({arg_names})
        _release_event_callback_ref(callback_ref)
        return result
'''

    retained_ref_methods = {
        # LVGL retains the canvas backing pointer.
        'canvas_set_buffer': {
            'slot': 'canvas_buffer',
            'ref_arg': 'buf',
            'append': False,
        },

        # lv_obj_add_style() stores the lv_style_t pointer; it does not copy
        # the style.  Keep the Python style wrapper alive independently of
        # the transient Python object wrapper.
        'obj_add_style': {
            'slot': 'styles',
            'ref_arg': 'style',
            'append': True,
        },
    }

    # Safe bulk release.  Individual obj_remove_style() is intentionally
    # conservative because the same style may still be attached with another
    # selector.
    release_ref_methods = {
        'obj_remove_style_all': 'styles',
    }

    for name in structs_unions.keys():
        output.write(f'{name} = _lvgl.{name}\n')

    output.write('\n\n')

    for item in other:
        output.write(f'{item} = _lvgl.{item}\n')

    output.write('\n\n')

    function_template = '''\
def {name}({args}){ret_val}:
    return _lvgl.{o_name}({arg_names})
'''

    obj_function_template = '''\
def {name}({args}){ret_val}:
    return _wrap_obj(_lvgl.{o_name}({arg_names}))
'''

    for func_name, func in list(functions.items()):
        new_params = []
        param_names = []

        sig = func.signature

        for param_name, param in list(sig.parameters.items()):
            if param.kind == param.VAR_POSITIONAL:
                param_name = f'*{param_name}'
                new_params.append(param_name)
            else:
                anno = convert_annotation(param.annotation)
                anno = anno.replace('NoneType', 'void')
                anno = convert_type(anno)
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        raw_return_annotation = convert_annotation(sig.return_annotation)
        returns_obj = (
            raw_return_annotation
            .replace('_lvgl.', '')
            .strip('"')
            == 'obj_t'
        )

        anno = convert_type(raw_return_annotation)
        ret_val = f' -> {anno}'

        template = obj_function_template if returns_obj else function_template

        fnc = template.format(
            name=func_name,
            o_name=func_name,
            args=', '.join(new_params),
            arg_names=', '.join(param_names),
            ret_val=ret_val
        )

        output.write('\n' + fnc + '\n')

    output.write('\n\n')


    struct_class_template = '''\
class {name}({parent_cls}):

{methods}'''

    for name, value in structs.items():
        methods = []

        for method_name, cont in value['methods'].items():
            if cont['name'] == 'timer_delete':
                meth = delete_timer_method_template.format(
                    name=method_name,
                    o_name=cont['name'],
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                )
            else:
                template = (
                    obj_method_template
                    if cont.get('returns_obj', False)
                    else method_template
                )

                meth = template.format(
                    name=method_name,
                    o_name=cont['name'],
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                )

            methods.append(meth)

        cls = struct_class_template.format(
            name=name,
            parent_cls=f'_lvgl.{name}',
            methods='\n'.join(methods) or '    pass',
        )

        output.write(cls + '\n\n')

    # Object/widget wrappers must be emitted independently of struct wrappers.
    for name, value in obj_classes.items():
        methods = []
        enms = []

        for method_name, cont in value['methods'].items():
            o_name = cont['name']

            if o_name in retained_ref_methods:
                retained = retained_ref_methods[o_name]
                meth = retained_ref_method_template.format(
                    name=method_name,
                    o_name=o_name,
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                    slot=retained['slot'],
                    ref_arg=retained['ref_arg'],
                    append_arg=', append=True' if retained['append'] else '',
                )

            elif o_name == 'obj_remove_event':
                meth = remove_event_method_template.format(
                    name=method_name,
                    o_name=o_name,
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                )

            elif o_name == 'obj_remove_event_dsc':
                meth = remove_event_dsc_method_template.format(
                    name=method_name,
                    o_name=o_name,
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                )

            elif o_name == 'obj_delete':
                meth = delete_obj_method_template.format(
                    name=method_name,
                    o_name=o_name,
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                )

            elif o_name in release_ref_methods:
                meth = release_ref_method_template.format(
                    name=method_name,
                    o_name=o_name,
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                    slot=release_ref_methods[o_name],
                )

            else:
                template = (
                    obj_method_template
                    if cont.get('returns_obj', False)
                    else method_template
                )

                meth = template.format(
                    name=method_name,
                    o_name=o_name,
                    args=cont['params'],
                    arg_names=cont['param_names'],
                    ret_val=cont['ret_val'],
                )

            methods.append(meth)

        for enum_cls_name, d in value['enums'].items():
            enm_items = []

            for item_name, data in d.items():
                o_enum_name = data[-1]
                enm_items.append(
                    enum_item_template.format(
                        name=item_name,
                        o_name=o_enum_name
                    )
                )

            if not enm_items:
                continue

            enm_cls = enum_template.format(
                name=enum_cls_name,
                items='\n'.join(enm_items)
            )

            enm_cls = '\n'.join(
                '    ' + line for line in enm_cls.split('\n')
            )
            enms.append(enm_cls)

        if enms:
            enms = '\n'.join(enms)
            enms += '\n'
        else:
            enms = ''

        cls = class_template.format(
            name=name,
            parent_cls=value['parent_cls'],
            enums=enms,
            args=value['args'],
            create_func_name=value['create_func_name'],
            arg_names=value['arg_names'],
            identity_methods=obj_identity_methods if name == 'obj' else '',
            methods='\n'.join(methods),
            fp='' if name == 'obj' else '_lvgl._DefaultArg'
        )

        output.write(cls + '\n\n')

    # Recover concrete widget wrapper types when LVGL APIs return lv_obj_t *.
    # This mirrors MicroPython binding behaviour for calls such as
    # obj.get_child(), which can return an image, label, button, etc.
    output.write('\n_obj_type_map = []\n')

    for obj_name in obj_classes:
        if obj_name == 'obj':
            continue

        output.write(
            f"if hasattr(_lvgl, {obj_name + '_class'!r}):\n"
        )
        output.write(
            f"    _obj_type_map.append("
            f"(_lvgl.{obj_name}_class, {obj_name}))\n"
        )

    # Base obj must come last in case the LVGL type predicate also accepts
    # derived object classes.
    output.write(
        'if hasattr(_lvgl, "obj_class"):\n'
        '    _obj_type_map.append((_lvgl.obj_class, obj))\n'
        '\n'
        '\n'
        'def _wrap_obj(value):\n'
        '    if value is None:\n'
        '        return None\n'
        '\n'
        '    for lv_class, py_class in _obj_type_map:\n'
        '        try:\n'
        '            if _lvgl.obj_check_type(value, lv_class):\n'
        '                instance = object.__new__(py_class)\n'
        '                value.cast(instance)\n'
        '                return instance\n'
        '        except Exception:\n'
        '            continue\n'
        '\n'
        '    return value\n'
        '\n'
    )

    # MicroPython lv_font_t function-pointer compatibility.
    #
    # In the MicroPython LVGL binding, font.get_glyph_dsc is the
    # lv_font_t.get_glyph_dsc function-pointer field itself and is called as:
    #
    #     font.get_glyph_dsc(font, dsc, letter, letter_next)
    #
    # mpy_builder normally turns lv_font_get_glyph_dsc() into a bound Python
    # method, whose calling convention is different. Built-in fonts created
    # while lvgl._raw is imported are also raw font_t instances, so install
    # this compatibility method on both classes.
    output.write(r"""
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

""")

    output.write(r"""
def _obj_set_grid_dsc_array(self, col_dsc, row_dsc):
    col_ref = _lvgl._make_c_array([int(value) for value in col_dsc], 'List[int32_t]')
    row_ref = _lvgl._make_c_array([int(value) for value in row_dsc], 'List[int32_t]')
    result = _lvgl.obj_set_grid_dsc_array(self, col_ref, row_ref)
    _retain_obj_ref(self, 'grid_columns', col_ref, append=False)
    _retain_obj_ref(self, 'grid_rows', row_ref, append=False)
    return result


obj.set_grid_dsc_array = _obj_set_grid_dsc_array
del _obj_set_grid_dsc_array

""")

    # LVGL retains button-matrix map pointers. Keep the actual _Array owner
    # alive, because pointer-array string storage lives in _Array.__refs.
    output.write(r"""
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

""")

    # LVGL retains keyboard map/control-map pointers. Keep the actual
    # _Array owners alive, because pointer-array string storage lives in
    # _Array.__refs.
    output.write(r"""
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

""")

    # MicroPython LVGL exposes animation path callbacks both as module-level
    # functions and as static members of anim_t, for example:
    #
    #     lv.anim_path_ease_in_out
    #     lv.anim_t.path_ease_in_out
    #
    anim_path_funcs = sorted(
        name
        for name in functions
        if name.startswith('anim_path_')
    )

    if anim_path_funcs:
        output.write('\n\n# Animation path callbacks\n')

        for func_name in anim_path_funcs:
            method_name = func_name.removeprefix('anim_')

            output.write(
                f'anim_t.{method_name} = staticmethod({func_name})\n'
            )

    output.close()

if __name__ == '__main__':
    if sys.platform == 'win32':
        run(r'..\build\lib.win-amd64-cpython-310')
    elif sys.platform == 'linux':
        run(r'build/lib.linux-x86_64-cpython-314')
