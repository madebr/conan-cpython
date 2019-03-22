# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.client.tools.oss import detected_os, detected_architecture
import os
import sys


class CPythonConan(ConanFile):
    name = "cpython"
    version = "3.7.2"
    description = "The Python programming language"
    topics = ("conan", "python", "programming", "language", "scripting")
    url = "https://github.com/bincrafters/conan-cpython"
    homepage = "https://www.python.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "PSF"

    exports = ("../cpython_common.py", )
    exports_sources = ("../config.site", "../LICENSE.md", )

    settings = "os", "arch", "compiler", "build_type"
    options = {  # FIXME: add curses readline
        "shared": [True, False],
        "fPIC": [True, False],
        "optimizations": [True, False],
        "lto": [True, False],
        "bz2": [True, False],
        "ctypes": [True, False],
        "decimal": [True, False],
        "dbm": [True, False],
        "expat": [True, False],
        "gdbm": [True, False],
        "lzma": [True, False],
        "nis": [True, False],
        "sqlite3": [True, False],
        "tkinter": [True, False],
        "uuid": [True, False],
        "ipv6": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "optimizations": False,
        "lto": False,
        "bz2": True,
        "ctypes": True,
        "dbm": True,
        "decimal": True,
        "expat": True,
        "gdbm": True,
        "lzma": True,
        "nis": True,
        "sqlite3": True,
        "tkinter": True,
        "uuid": True,
        "ipv6": True,
    }

    _source_subfolder = "sources"

    _common = None
    def _add_common(self):
        curdir = os.path.dirname(os.path.realpath(__file__))
        pardir = os.path.dirname(curdir)
        sys.path.insert(0, curdir)
        sys.path.insert(0, pardir)
        from cpython_common import CPythonCommon
        self._common = CPythonCommon(self, False)

    def configure(self):
        self._add_common()
        self._common.configure()

    def config_options(self):
        self._add_common()
        self._common.config_options()

    def build_requirements(self):
        self._add_common()
        self._common.build_requirements()

    def requirements(self):
        self._add_common()
        self._common.requirements()

    def source(self):
        self._add_common()
        self._common.source()

    def build(self):
        self._add_common()
        self._common.build()

    def package(self):
        self._add_common()
        self._common.package()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]

        self.user_info.VERSION = self.version
