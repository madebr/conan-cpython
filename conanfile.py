# -*- coding: utf-8 -*-

from conans import tools
from conanfile_base import CPythonBaseConanFile


class CPythonConan(CPythonBaseConanFile):
    name = CPythonBaseConanFile._base_name
    version = CPythonBaseConanFile.version

    exports = CPythonBaseConanFile.exports + ("conanfile_base.py", )

    options = CPythonBaseConanFile._base_options
    default_options = CPythonBaseConanFile._base_default_options
    settings = "os", "arch", "compiler", "build_type"

    _is_installer = False

    @property
    def _os(self):
        return self.settings.os

    @property
    def _arch(self):
        return self.settings.arch

    @property
    def _build_type(self):
        return self.settings.build_type

    def _options(self, key):
        return getattr(self.options, key)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        
        self.user_info.VERSION = self.version
