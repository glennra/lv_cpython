# -*- coding: utf-8 -*-

import os
import sys
from setuptools.command.build import build as _build  # NOQA

import shutil
from . import py_builder
from . import mpy_builder


class build(_build):
    ast = None
    model = None
    sdl2_dll = None
    extra_includes = []

    user_options = [
        ('debug', None, 'adds debugging output to the compilation')
    ] + _build.user_options

    boolean_options = ['debug'] + _build.boolean_options

    def finalize_options(self):
        _build.finalize_options(self)
        self.distribution.include_dirs = self.extra_includes

    def run(self):
        generated = False

        # build_py must populate build_lib before we replace the checked-in
        # generated files there.  Generate immediately afterwards, before
        # build_ext compiles the native extension.
        for command_name in self.get_sub_commands():
            if command_name == 'build_ext':
                self._generate_bindings()
                generated = True

            self.run_command(command_name)

        # Keep this command useful for distributions without an extension
        # subcommand as well.
        if not generated:
            self._generate_bindings()

        self._relocate_windows_extension()

    def _generate_bindings(self):
        lvgl_output_path = os.path.join(self.build_lib, 'lvgl')
        os.makedirs(lvgl_output_path, exist_ok=True)

        py_builder.run(lvgl_output_path, self.model)
        mpy_builder.run(self.build_lib, self.model)

    def _relocate_windows_extension(self):
        """Place Windows build products beside the Python package.

        This relocation remains necessary for the installed package layout;
        generation no longer depends on it.
        """

        lvgl_output_path = os.path.join(self.build_lib, 'lvgl')

        for file in os.listdir(self.build_lib):
            if file.endswith('pyd') or file.endswith('pdb'):
                src = os.path.join(self.build_lib, file)
                dst = os.path.join(lvgl_output_path, file)
                if os.path.exists(dst):
                    os.remove(dst)

                shutil.copyfile(src, dst)
                os.remove(src)

        if sys.platform.startswith('win'):
            dst = os.path.join(lvgl_output_path, 'SDL2.dll')

            if os.path.exists(dst):
                os.remove(dst)

            shutil.copyfile(self.sdl2_dll, dst)
