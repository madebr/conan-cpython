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
    exports_sources = ("../config.site", )

    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = "sources"

    def _is_crosscompile(self):
        return self._os() != detected_os or self._arch() != detected_architecture

    def _os(self):
        return self.settings.os

    def _arch(self):
        return self.settings.arch

    def _build_type(self):
        return self.settings.build_type

    def _python_regen(self):
        return os.path.join(self.deps_cpp_info["cpython_installer"].bin_paths[0], "python")

    def configure(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_configure
        cpython_configure(self)

    def config_options(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_config_options
        cpython_config_options(self)

    def build_requirements(self):
        if self._is_crosscompile():
            self.output.info("Cross compilation detected: need cpython_installer")
            self.build_requires("cpython_installer/{}@{}/{}".format(self.version, self.user, self.channel))

    def requirements(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_get_requirements
        for req in cpython_get_requirements(self):
            self.requires(req)

    def source(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_source
        cpython_source(self)

    def package(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_package
        cpython_package(self)

    def build(self):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        from cpython_common import cpython_build
        cpython_build(self)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]

        self.user_info.VERSION = self.version


try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    from cpython_common import cpython_options, cpython_default_options
    CPythonConan.options = cpython_options()
    CPythonConan.default_options = cpython_default_options()
except ImportError:
    CPythonConan.options = []
    CPythonConan.default_options = []
