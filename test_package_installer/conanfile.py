# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from io import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_CPYTHON_VERSION"] = self.deps_user_info["cpython_installer"].VERSION
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="lib", src="lib")

    def test(self):
        if not tools.cross_building(self.settings):
            cmake = CMake(self)
            cmake.test()

        assert tools.which("python3").startswith(str(self.deps_cpp_info["cpython_installer"].rootpath))
