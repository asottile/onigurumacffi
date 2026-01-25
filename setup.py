from __future__ import annotations

import platform
import sys
import sysconfig

from setuptools import setup

if (
        platform.python_implementation() == 'CPython' and
        sysconfig.get_config_var('Py_GIL_DISABLED') != 1
):
    try:
        import wheel.bdist_wheel
    except ImportError:
        cmdclass = {}
    else:
        class bdist_wheel(wheel.bdist_wheel.bdist_wheel):
            def finalize_options(self) -> None:
                self.py_limited_api = f'cp3{sys.version_info[1]}'
                super().finalize_options()

        cmdclass = {'bdist_wheel': bdist_wheel}
else:
    cmdclass = {}

setup(cffi_modules=['onigurumacffi_build.py:ffibuilder'], cmdclass=cmdclass)
