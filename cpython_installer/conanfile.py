# -*- coding: utf-8 -*-

from conans import ConanFile
from conans.client.tools.oss import detected_os, detected_architecture
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

    exports = ("../cpython_common.py")

    settings = "os_build", "arch_build", "compiler"

    _source_subfolder = "sources"

    def _os(self):
        return self.settings.os_build

    def _arch(self):
        return self.settings.arch_build

    def _is_crosscompile(self):
        return self._os() != detected_os or self._arch() != detected_architecture

    def _build_type(self):
        return "Release"

    def _python_regen(self):
        raise Exception("cpython_installer cannot be cross built")

    def config_options(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_config_options
        cpython_config_options(self)

    def build_requirements(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_get_requirements
        for req in cpython_get_requirements(self):
            self.build_requires(req)
        if self._is_crosscompile():
            raise Exception("cpython_installer cannot be cross built")

    def source(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_source
        cpython_source(self)

    def build(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_build
        cpython_build(self)

    def package(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_package
        cpython_package(self)

        shutil.rmtree(os.path.join(self.package_folder, "include"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        self.user_info.VERSION = self.version


try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    from cpython_common import cpython_options, cpython_default_options
    CPythonInstallerConan.options = cpython_options()
    CPythonInstallerConan.default_options = cpython_default_options()
except ImportError:
    CPythonInstallerConan.options = []
    CPythonInstallerConan.default_options = []
