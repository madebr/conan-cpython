from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class CpythonConan(ConanFile):
    name = "cpython"
    version = "3.6.4"
    license = "Python"
    url = "https://www.python.org"
    description = "The Python programming language"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "optimizations": [True, False],
        "ipv6": [True, False],
    }
    default_options = "shared=False", "optimizations=False", "ipv6=True",
    generators = "cmake"

    @property
    def is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def build_requirements(self):
        self.requires('lzma/5.2.3@bincrafters/stable')

    def source(self):
        source_url = "https://www.python.org/ftp/python/{0}/Python-{0}.tgz".format(self.version)
        tools.get(source_url)
        extracted_dir = "Python-{0}".format(self.version)
        os.rename(extracted_dir, "sources")

    def build(self):
        with tools.chdir("sources"):
            prefix = tools.unix_path(self.package_folder) if self.settings.os == "Windows" else self.package_folder
            args = ["--prefix=%s" % prefix]
            if self.options.shared:
                args.append("--enable-shared")
            if self.settings.build_type == "Debug":
                args.extend(["--with-pydebug", "--with-assertions"])
            else:
                args.extend(["--without-pydebug", "--without-assertions"])
            if self.options.optimizations:
                args.extend(["--enable-optimizations", "--with-lto"])
            else:
                args.extend(["--disable-optimizations"])
            if self.options.ipv6:
                args.extend(["--enable-ipv6"])
            else:
                args.extend(["--disable-ipv6"])
            env_vars = {
                "PKG_CONFIG": os.path.abspath("pkg-config"),
            }
            if self.is_msvc:
                env_vars.update({
                    "CFLAGS": str(self.settings.compiler.runtime),
                    "CPPFLAGS": str(self.settings.compiler.runtime),
                    "LDFLAGS": str(self.settings.compiler.runtime),
                })

            with tools.environment_append(env_vars):
                env_build = AutoToolsBuildEnvironment(self, win_bash=self.is_mingw)

                env_build.configure(args=args)
                env_build.make()
                env_build.make(args=["install"])

    def package(self):
        self.copy("*", src="include", dst="include")
        self.copy("*", src="bin", dst="bin")
        self.copy("*", src="lib", dst="lib")

    def package_info(self):
        python_name = "python{0}m".format(self.version[:self.version.rfind(".")])
        self.cpp_info.libs = [python_name]
        self.cpp_info.includedirs = ["include/{0}".format(python_name)]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
