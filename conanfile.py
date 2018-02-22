from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class CpythonConan(ConanFile):
    name = "cpython"
    version = "3.6.4"
    url = "https://www.python.org"
    description = "The Python programming language"
    license = "Python"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "optimizations": [True, False],
        "ipv6": [True, False],
    }
    default_options = "shared=False", "optimizations=False", "ipv6=True",

    @property
    def is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def build_requirements(self):
        self.requires('lzma/5.2.3@bincrafters/stable')

    def source(self):
        source_url = "https://www.python.org/ftp/python/{0}/Python-{0}.tgz".format(self.version)
        tools.get(source_url)
        extracted_dir = "Python-{0}".format(self.version)
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_with_msvc()
        else:
            if self.is_mingw:
                #add code later if mingw support is required
                pass
            else:
                self.build_with_make()
            

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_subfolder)
        self.copy("*", src="include", dst="include")
        self.copy("*", src="bin", dst="bin")
        self.copy("*", src="lib", dst="lib")

    def package_info(self):
        python_name = "python{0}m".format(self.version[:self.version.rfind(".")])
        self.cpp_info.libs = [python_name]
        self.cpp_info.includedirs = ["include/{0}".format(python_name)]
        
    def build_with_msvc(self):
        with tools.chdir(os.path.join(self.source_subfolder, "PCBuild")):
            build_type = self.settings.build_type
            arch = 'x64' if self.settings.arch == 'x86_64' else 'Win32'
            self.run('build.bat -c {build_type} -p {arch}'.format(build_type=build_type, arch=arch))
        
    def build_with_make(self):
        with tools.chdir(self.source_subfolder):
            args = ["--prefix=%s" % tools.unix_path(self.package_folder)]
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

            with tools.environment_append(env_vars):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure(args=args)
                env_build.make()
                env_build.make(args=["install"])

