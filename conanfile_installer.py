# -*- coding: utf-8 -*-

from conanfile_base import CPythonBaseConanFile
import os


class CPythonConan(CPythonBaseConanFile):
    name = CPythonBaseConanFile._base_name + "_installer"
    version = CPythonBaseConanFile.version

    exports = CPythonBaseConanFile.exports + ("conanfile_base.py", )

    settings = "os_build", "arch_build", "compiler"

    _is_installer = True

    @property
    def _os(self):
        return self.settings.os_build

    @property
    def _arch(self):
        return self.settings.arch_build

    @property
    def _build_type(self):
        return "Release"

    def _options(self, key):
        return self._base_default_options[key]

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.user_info.VERSION = self.version

        self.user_info.CPYTHON_BIN = os.path.join(self.package_folder, "bin", "python")
