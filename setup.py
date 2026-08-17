# setup.py
import os
import sys
import re

project_path = os.path.dirname(__file__)
sys.path.insert(0, project_path)

from pycparser import c_ast, c_generator  # NOQA
import cffi  # NOQA

from setuptools import setup
from builder import ast_builder, binding_model, utils, build, build_ext, install


if '--debug' in sys.argv:
    debug = True
    sys.argv.remove('--debug')
else:
    debug = False


build_path = os.path.relpath(os.path.join(project_path, 'build'))
build_temp = os.path.join(build_path, 'temp')

lvgl_path = os.path.relpath(os.path.join(project_path, 'src', 'lvgl'))
lvgl_src_path = os.path.join(lvgl_path, 'src')

if not os.path.exists(build_temp):
    os.makedirs(build_temp)


library_dirs = []
include_dirs = ['.']
linker_args = []
libraries = ['SDL2']
cpp_args = ['-DCPYTHON_SDL']

sanitizers = [
    item.strip()
    for item in os.environ.get('LV_SANITIZERS', '').split(',')
    if item.strip()
]
unsupported_sanitizers = set(sanitizers) - {'address', 'undefined'}
if unsupported_sanitizers:
    raise RuntimeError(
        'Unsupported LV_SANITIZERS value(s): '
        + ', '.join(sorted(unsupported_sanitizers))
    )


if sys.platform.startswith('win'):
    if sanitizers:
        raise RuntimeError('LV_SANITIZERS is not supported on Windows')

    from builder import get_sdl2

    import pyMSVC  # NOQA

    environment = pyMSVC.setup_environment()
    print(environment)

    sdl2_include, sdl2_dll = get_sdl2.get_sdl2(build_temp)
    include_dirs += [sdl2_include]
    library_dirs += [os.path.split(sdl2_dll)[0]]
    libraries.append('legacy_stdio_definitions')

    build.sdl2_dll = sdl2_dll
    cpp_args.insert(0, '-std:c11')
    cpp_args.extend([
        '/wd4996',
        '/wd4244',
        '/wd4267'
    ])

    if debug:
        linker_args.append('/DEBUG')
        cpp_args.append('/Zi')


elif sys.platform.startswith('darwin'):
    cpp_args.insert(0, '-std=c11')

    if debug:
        cpp_args.append('-ggdb')


else:
    cpp_args.insert(0, '-std=c11')
    cpp_args.append('-Wno-incompatible-pointer-types')
    if debug:
        cpp_args.append('-ggdb')


if sanitizers:
    sanitizer_flag = '-fsanitize=' + ','.join(sanitizers)
    cpp_args.extend([sanitizer_flag, '-fno-omit-frame-pointer'])
    linker_args.append(sanitizer_flag)



build.extra_includes = include_dirs



# some paths/files we do not need to compile the source files for.
IGNORE_DIRS = (
    'disp', 'arm2d', 'gd32_ipa', 'nxp', 'stm32_dma2d', 'swm341_dma2d'
)
IGNORE_FILES = ()


# # function that iterates over the LVGL/src directory to
# locate all of the ".c" files as these files need to be compiled
def iter_sources(p):
    res = []  # NOQA
    folders = []
    for f in os.listdir(p):  # NOQA
        file = os.path.join(p, f)
        if os.path.isdir(file):
            if f in IGNORE_DIRS:
                continue

            folders.append(file)
        elif f not in IGNORE_FILES:
            if not f.endswith('.c'):
                continue

            res.append(file)

    for folder in folders:
        res.extend(iter_sources(folder))

    return res


# monkeypatched functions in pycparser.c_generator.CGenerator
# I used the CGenerator to output declarations that CFFI uses to make
# the Python C extension. I am using only the header files and not the C
# source files for the preprocessing. There are however some functions that are
# defined in the header files and I needed to change those to declaractions.

# this function removes any of the declarations that get added from the
# fake lib c header files. we do not wnat to use that information because it
# declares things like uint_8t as int which it 3 bytes larger then it should be.
# this causes problems in the c extension.
def visit(self, node):
    if utils.is_lib_c_node(node):
        return ''

    method = f'visit_{node.__class__.__name__}'
    ret = getattr(self, method, self.generic_visit)(node)
    return '' if ret.strip() == ';' else ret


# turns function definitions into declarations.
def visit_FuncDef(self, n):
    decl = self.visit(n.decl)  # NOQA
    self.indent_level = 0
    if n.param_decls:
        knrdecls = ';\n'.join(self.visit(p) for p in n.param_decls)
        res = decl + '\n' + knrdecls + ';\n'
    else:
        res = decl + ';\n'

    return res


callback_names = []


def visit_Typedef(self, n):
    s = ''
    if n.storage:
        s += ' '.join(n.storage) + ' '

    s += self._generate_type(n.type)

    node = n
    for type_ in (
        c_ast.PtrDecl,
        c_ast.FuncDecl,
        (c_ast.TypeDecl, c_ast.PtrDecl)
    ):
        if isinstance(node.type, type_):
            node = node.type
        else:
            return s

    while isinstance(node, c_ast.PtrDecl):
        node = node.type

    name = node.declname
    for item in ('_cb_t', '_f_t'):
        if not name.endswith(item):
            continue

        if f'py_{name}' in callback_names:
            return ''

        callback_names.append(f'py_{name}')

        s = s.replace(f'(*{name})', f'py_{name}') + ';\n' + s

        if s.startswith('typedef'):
            s = '\n\nextern "Python"' + s[7:]
        else:
            s = '\n\nextern "Python"' + s

        break

    return s


# LVGL 9.4 declares the lv_fs_drv_t callbacks directly as function-pointer
# struct members rather than as named *_cb_t typedefs. CFFI extern-Python
# callbacks need names, so synthesize stable names for those members.
_ANONYMOUS_CALLBACK_STRUCTS = {'_lv_fs_drv_t'}


def _anonymous_struct_callback_name(struct_name, field_name):
    if (
        struct_name not in _ANONYMOUS_CALLBACK_STRUCTS
        or not field_name
    ):
        return None

    struct_name = struct_name.lstrip('_')
    if struct_name.endswith('_t'):
        struct_name = struct_name[:-2]

    # _lv_fs_drv_t + open_cb -> lv_fs_drv_open_cb_t
    return f'{struct_name}_{field_name}_t'


def _build_anonymous_struct_callback_cdefs(ast, generator):
    declarations = []
    seen = set()

    class Visitor(c_ast.NodeVisitor):
        def visit_Struct(self, node):
            if (
                node.name not in _ANONYMOUS_CALLBACK_STRUCTS
                or not node.decls
            ):
                return

            for field in node.decls:
                if not isinstance(field, c_ast.Decl):
                    continue
                if not isinstance(field.type, c_ast.PtrDecl):
                    continue
                if not isinstance(field.type.type, c_ast.FuncDecl):
                    continue

                callback_name = _anonymous_struct_callback_name(
                    node.name,
                    field.name,
                )
                if callback_name is None or callback_name in seen:
                    continue

                declaration = generator.visit(field).strip().rstrip(';')

                # pycparser emits forms such as:
                #   void *(*open_cb)(...)
                #   bool (*ready_cb)(...)
                pattern = re.compile(
                    r'\(\s*\*\s*' + re.escape(field.name) + r'\s*\)'
                )
                declaration, replacements = pattern.subn(
                    f'py_{callback_name}',
                    declaration,
                    count=1,
                )

                if replacements != 1:
                    raise RuntimeError(
                        'Unable to synthesize extern-Python declaration for '
                        f'{node.name}.{field.name}: {declaration!r}'
                    )

                declarations.append(
                    f'extern "Python" {declaration};'
                )
                seen.add(callback_name)

    Visitor().visit(ast)
    return declarations


CDEF = """
#define INT32_MAX 2147483647
typedef char* va_list;

{ast}

"""

# Parse LVGL headers once using the shared AST builder.  This same parser
# is used by builder.regenerate, so editable builds and fast regeneration
# cannot silently diverge.
ast = ast_builder.run(project_path, debug=debug)
build.ast = ast
build.model = binding_model.build_binding_model(
    ast,
    symbol_header=os.path.join(
        project_path,
        'src',
        'lvgl',
        'src',
        'font',
        'lv_symbol_def.h',
    ),
)


# saving the old generator functions so they can be put
# back in place before cffi runs. cffi uses pycparser and I do not
# know if it uses the generator at all. so better safe then sorry
old_visit = c_generator.CGenerator.visit
old_visit_FuncDecl = c_generator.CGenerator.visit_FuncDecl
old_visit_Typedef = c_generator.CGenerator.visit_Typedef

# putting the updated functions in place
setattr(c_generator.CGenerator, 'visit', visit)
setattr(c_generator.CGenerator, 'visit_FuncDef', visit_FuncDef)
setattr(c_generator.CGenerator, 'visit_Typedef', visit_Typedef)

generator = c_generator.CGenerator()
ffibuilder = cffi.FFI()

# Generate declarations while custom CGenerator patches are active.
cdef = CDEF.format(ast=str(generator.visit(ast)))

anonymous_callback_cdefs = _build_anonymous_struct_callback_cdefs(
    ast,
    generator,
)
if anonymous_callback_cdefs:
    cdef += '\n\n' + '\n'.join(anonymous_callback_cdefs) + '\n'

# Restore pycparser BEFORE giving anything to CFFI.
setattr(c_generator.CGenerator, 'visit', old_visit)
setattr(
    c_generator.CGenerator,
    'visit_FuncDecl',
    old_visit_FuncDecl,
)
setattr(
    c_generator.CGenerator,
    'visit_Typedef',
    old_visit_Typedef,
)

# Existing cleanup.
cdef = '\n'.join(
    line
    for line in cdef.split('\n')
    if line.strip() != ';'
)


# ---------------------------------------------------------------------------
# lv_obj_class_t globals
# ---------------------------------------------------------------------------

# lv_obj_class_t is opaque to CFFI.  Globals of this type cannot be
# accessed by value, so remove them and expose pointer-returning helpers.

obj_class_pattern = re.compile(
    r'^\s*'
    r'(?:extern\s+)?'
    r'const\s+'
    r'(?:lv_obj_class_t|struct\s+_lv_obj_class_t)\s+'
    r'(lv_[A-Za-z0-9_]+_class)\s*;'
    r'\s*$'
)

obj_class_symbols = []
filtered_cdef = []

for line in cdef.splitlines():
    match = obj_class_pattern.match(line)

    if match:
        print("Removing CFFI object-class global:", line)
        obj_class_symbols.append(match.group(1))
    else:
        filtered_cdef.append(line)

obj_class_symbols = sorted(set(obj_class_symbols))

print(f"Found {len(obj_class_symbols)} object-class globals")

cdef = '\n'.join(filtered_cdef)

# Replace inaccessible globals with helper-function declarations.
cdef += '\n\n' + '\n'.join(
    f'const lv_obj_class_t *py_get_{name}(void);'
    for name in obj_class_symbols
) + '\n'

# Exact sanity check.
leftovers = [
    line
    for line in cdef.splitlines()
    if obj_class_pattern.match(line)
]

if leftovers:
    raise RuntimeError(
        "lv_obj_class_t globals remain in CFFI cdef:\n"
        + '\n'.join(leftovers)
    )


# putting the old functions back in place
setattr(c_generator.CGenerator, 'visit', old_visit)
setattr(c_generator.CGenerator, 'visit_FuncDecl', old_visit_FuncDecl)
setattr(c_generator.CGenerator, 'visit_Typedef', old_visit_Typedef)

# my monkey patchs were not perfect and when I removed all of the
# typedefs put in place from the fake lib c header files
# I was not able to remove the trailing semicolon. So that is what is
# being done here.
filtered_cdef = []
seen_function_declarations = set()
for line in cdef.split('\n'):
    stripped = line.strip()
    if stripped == ';':
        continue
    if '(' in stripped and stripped.endswith(');') and not stripped.startswith('typedef'):
        if stripped in seen_function_declarations:
            continue
        seen_function_declarations.add(stripped)
    filtered_cdef.append(line)
cdef = '\n'.join(filtered_cdef)

cdef += r"""
int py_sdl_get_display_size(
    int display_index,
    int *width,
    int *height
);
const char *py_sdl_get_error(void);
"""

# set the definitions into cffi
ffibuilder.cdef(cdef)

obj_class_helper_source = '\n'.join(
    f'const lv_obj_class_t *py_get_{name}(void) '
    f'{{ return &{name}; }}'
    for name in obj_class_symbols
)

sdl_helper_source = r"""
#if LV_USE_SDL

#include LV_SDL_INCLUDE_PATH

int py_sdl_get_display_size(
    int display_index,
    int *width,
    int *height
)
{
    SDL_DisplayMode mode;
    int display_count;

    if(width == NULL || height == NULL) {
        SDL_SetError("width and height pointers must not be NULL");
        return -1;
    }

    /*
     * This function is intended to be called before
     * lv_sdl_window_create(), so initialize SDL video if necessary.
     */
    if((SDL_WasInit(SDL_INIT_VIDEO) & SDL_INIT_VIDEO) == 0) {
        if(SDL_InitSubSystem(SDL_INIT_VIDEO) != 0) {
            return -1;
        }
    }

    display_count = SDL_GetNumVideoDisplays();

    if(display_count < 0) {
        return -1;
    }

    if(
        display_index < 0 ||
        display_index >= display_count
    ) {
        SDL_SetError(
            "display index %d out of range; display count is %d",
            display_index,
            display_count
        );
        return -1;
    }

    if(SDL_GetCurrentDisplayMode(display_index, &mode) != 0) {
        return -1;
    }

    *width = mode.w;
    *height = mode.h;

    return 0;
}


const char *py_sdl_get_error(void)
{
    return SDL_GetError();
}

#else

int py_sdl_get_display_size(
    int display_index,
    int *width,
    int *height
)
{
    (void)display_index;
    (void)width;
    (void)height;

    return -1;
}


const char *py_sdl_get_error(void)
{
    return "LVGL SDL support is disabled";
}

#endif
"""


native_helper_source = (
    obj_class_helper_source
    + '\n'
    + sdl_helper_source
)

# set the name of the c extension and also tell cffi what
# we need to compile
ffibuilder.set_source(
    '__lib_lvgl',
    '''
#include "src/lvgl/demos/lv_demos.h"

%s''' % native_helper_source,
    sources=(
            iter_sources(lvgl_src_path) +
            iter_sources(os.path.join(lvgl_path, 'demos'))
    ),
    define_macros=[('CPYTHON_SDL', 1)],
    library_dirs=library_dirs,
    libraries=libraries,
    # include_dirs=include_dirs + [project_path, lvgl_path],
    include_dirs=include_dirs + [
        project_path,
        os.path.join(project_path, 'src'),
        os.path.join(project_path, 'src', 'lvgl'),
    ],    
    extra_compile_args=cpp_args,
    extra_link_args=linker_args,
    language='c'
)


ext_modules = [ffibuilder.distutils_extension()]

setup(
    name='lvgl',
    author='Kevin G. Schlosser, Glenn Ramsey',
    version='0.1.2',
    zip_safe=False,
    packages=['lvgl'],
    install_requires=['cffi>=1.15.1'],
    ext_modules=ext_modules,
    cmdclass=dict(build=build, build_ext=build_ext, install=install)
)
