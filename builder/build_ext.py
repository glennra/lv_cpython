# -*- coding: utf-8 -*-

import os

from setuptools.command.build_ext import build_ext as _build_ext

from . import mpy_builder, py_builder
from .build import build


class build_ext(_build_ext):
    """Generate the Python bindings for PEP 660 editable installs."""

    ast = None

    def run(self):
        if getattr(self, 'editable_mode', False):
            project_path = os.path.abspath(
                os.path.dirname(os.path.dirname(__file__))
            )
            lvgl_output_path = os.path.join(project_path, 'lvgl')

            py_builder.run(lvgl_output_path, build.model)
            mpy_builder.run(project_path, build.model)

        _build_ext.run(self)
