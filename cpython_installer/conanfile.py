# -*- coding: utf-8 -*-

from conans import ConanFile
import os
import shutil
import sys


class CPythonInstallerConan(ConanFile):
    name = "cpython_installer"
    version = "3.7.2"
    description = "The Python programming language"
    topics = ("conan", "python", "programming", "language", "scripting")
    url = "https://github.com/bincrafters/conan-cpython"
    homepage = "https://www.python.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "PSF"

    exports = ("../cpython_common.py", )
    exports_sources = ("../config.site", "../LICENSE.md", )

    settings = "os_build", "arch_build", "compiler"

    _source_subfolder = "sources"

    _common = None
    def _add_common(self):
        curdir = os.path.dirname(os.path.realpath(__file__))
        pardir = os.path.dirname(curdir)
        sys.path.insert(0, curdir)
        sys.path.insert(0, pardir)
        from cpython_common import CPythonCommon
        self._common = CPythonCommon(self, True)

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

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        self.user_info.VERSION = self.version

        self.user_info.CPYTHON_BIN = os.path.join(self.package_folder, "bin", "python")
