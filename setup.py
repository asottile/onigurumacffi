from __future__ import annotations

import platform
import sys
import sysconfig

from setuptools import setup

if (
        platform.python_implementation() == 'CPython' and
        sysconfig.get_config_var('Py_GIL_DISABLED') != 1
):
    options = {'bdist_wheel': {'py_limited_api': f'cp3{sys.version_info[1]}'}}
else:
    options = {}

setup(cffi_modules=['onigurumacffi_build.py:ffibuilder'], options=options)
