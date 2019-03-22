# -*- coding: utf-8 -*-

from conans import AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import detected_architecture, get_env
from conans.client.tools.oss import detected_os
import os
import shutil
import tempfile


class CPythonCommon:
    def __init__(self, conanfile, is_installer):
        self.conanfile = conanfile
        self.is_installer = is_installer

    @property
    def os(self):
        if self.is_installer:
            return self.conanfile.settings.os_build
        else:
            return self.conanfile.settings.os

    @property
    def arch(self):
        if self.is_installer:
            return self.conanfile.settings.arch_build
        else:
            return self.conanfile.settings.arch

    @property
    def build_type(self):
        if self.is_installer:
            return "Release"
        else:
            return self.conanfile.settings.build_type

    @property
    def is_minw(self):
        return self.os == "Windows" and self.conanfile.settings.compiler == "gcc"

    @property
    def version_major_minor(self):
        return ".".join(self.conanfile.version.split(".")[:2])

    @property
    def cross_compiling(self):
        return self.os != detected_os() or self.arch != detected_architecture()

    @property
    def python_for_regen(self):
        if self.is_installer:
            raise Exception("installer cannot be cross built: no python executable for regen available")
        else:
            return self.deps_user_info["cpython_installer"].CPYTHON_BIN

    def get_option(self, key):
        if self.is_installer:
            installer_defaults = {
                "shared": False,
                "fPIC": True,
                "optimizations": False,
                "lto": False,
            }
            return installer_defaults.get(key, True)
        else:
            return getattr(self.conanfile.options, key)

    def configure(self):
        if self.is_installer and self.cross_compiling:
            raise ConanInvalidConfiguration("installer cannot be cross built")
        del self.conanfile.settings.compiler.libcxx

    def config_options(self):
        if not self.is_installer:
            # FIXME: move to cpython
            if self.conanfile.options.shared:
                del self.conanfile.options.fPIC
            if self.os in ("Windows", "Macos"):
                del self.conanfile.options.nis

    def requirements(self):
        self.conanfile.requires("OpenSSL/1.1.1a@conan/stable")
        if self.get_option("bz2"):
            self.conanfile.requires("bzip2/1.0.6@conan/stable")
        if self.get_option("ctypes"):
            self.conanfile.requires("libffi/3.2.1@bincrafters/stable")
        if self.get_option("dbm"):
            self.conanfile.requires("libdb/5.3.28@bincrafters/stable")  # FIXME: submit to bincrafters
        if self.get_option("decimal"):
            self.conanfile.requires("mpdecimal/2.4.2@bincrafters/stable")  # FIXME: submit to bincrafters
        if self.get_option("expat"):
            self.conanfile.requires("expat/2.2.5@bincrafters/stable")
        if self.get_option("gdbm"):
            self.conanfile.requires("gdbm/1.18.1@bincrafters/stable")  # FIXME: submit to bincrafters
        if self.get_option("lzma"):
            self.conanfile.requires("lzma/5.2.3@bincrafters/stable")
        if self.get_option("nis"):
            self.conanfile.requires("libnsl2/1.2.0@bincrafters/stable")  # FIXME: submit to bincrafters
        if self.get_option("sqlite3"):
            self.conanfile.requires("sqlite3/3.25.3@bincrafters/stable")
        if self.get_option("tkinter"):
            self.conanfile.requires("tk/8.6.9.1@bincrafters/stable")  # FIXME: submit to bincrafters
        if self.get_option("uuid"):
            self.conanfile.requires("libuuid/1.0.3@bincrafters/stable")

    def build_requirements(self):
        if not self.is_installer:
            self.conanfile.build_requires("cpython_installer/{}@{}/{}".format(self.conanfile.version, self.conanfile.user, self.conanfile.channel))

    def source(self):
        filename = "Python-{}.tgz".format(self.conanfile.version)
        url = "https://www.python.org/ftp/python/{}/{}".format(self.conanfile.version, filename)
        sha256 = "f09d83c773b9cc72421abba2c317e4e6e05d919f9bcf34468e192b6a6c8e328d"

        dlfilepath = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(dlfilepath) and not get_env("CPYTHON_FORCE_DOWNLOAD", False):
            self.conanfile.output.info("Skipping download. Using cached {}".format(dlfilepath))
        else:
            tools.download(url, dlfilepath)
        tools.check_sha256(dlfilepath, sha256)
        tools.untargz(dlfilepath)
        os.rename("Python-{}".format(self.conanfile.version), self.conanfile._source_subfolder)

        # fix library name of mpdecimal
        tools.replace_in_file(os.path.join(self.conanfile.source_folder, self.conanfile._source_subfolder, "setup.py"),
                              ":libmpdec.so.2", "libmpdec")
        tools.replace_in_file(os.path.join(self.conanfile.source_folder, self.conanfile._source_subfolder, "setup.py"),
                              "libraries = ['libmpdec']", "libraries = ['mpdec']")

        # on building x86 python on x86_64: readlink is just fine
        # tools.replace_in_file(os.path.join(self.conanfile.source_folder, self.conanfile._source_subfolder, "configure"),
        #                       "as_fn_error $? \"readelf for the host is required for cross builds\"",
        #                       "# as_fn_error $? \"readelf for the host is required for cross builds\"")

        makefile = os.path.join(self.conanfile.source_folder, self.conanfile._source_subfolder, "Makefile.pre.in")
        tools.replace_in_file(makefile,
                              "@OPT@",
                              "@OPT@ @CFLAGS@")

    def build(self):
        if self.conanfile.settings.compiler == "Visual Studio":
            self.build_msvc()
        else:
            self.build_autotools()

    def build_autotools(self):
        autotools = AutoToolsBuildEnvironment(self.conanfile)
        autotools.target = autotools.host

        if self.get_option("uuid"):
            autotools.include_paths += ["{}/uuid".format(d) for d in self.conanfile.deps_cpp_info["libuuid"].includedirs]
        args = [
            "--enable-shared" if self.get_option("shared") else "--disable-shared",
            "--with-gcc", "--without-icc",
            "--with-system-expat" if self.get_option("expat") else "--without-system-expat",
            "--with-system-libmpdec" if self.get_option("decimal") else "--without-system-libmpdec",
            "--enable-optimizations" if self.get_option("optimizations") else "--disable-optimizations",
            "--with-lto" if self.get_option("lto") else "--without-lto",
            "--enable-ipv6" if self.get_option("ipv6") else "--disable-ipv6",
            "--with-openssl={}".format(self.conanfile.deps_cpp_info["OpenSSL"].rootpath),
        ]
        if self.build_type == "Debug":
            args.extend(["--with-pydebug", "--with-assertions"])
        else:
            args.extend(["--without-pydebug", "--without-assertions"])
        if self.get_option("tkinter"):
            tcltk_includes = []
            tcltk_libs = []
            for dep in ("tcl", "tk", "zlib"):
                tcltk_includes += ["-I{}".format(d) for d in self.conanfile.deps_cpp_info[dep].includedirs]
                tcltk_libs += ["-l{}".format(lib) for lib in self.conanfile.deps_cpp_info[dep].libs]
            args.extend([
                "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
                "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
            ])
        env_vars = {
            "PKG_CONFIG": os.path.abspath("pkg-config"),
        }
        if self.cross_compiling:
            env_vars.update({
                "PYTHON_FOR_REGEN": self.python_for_regen,
                "CONFIG_SITE": os.path.join(self.conanfile.source_folder, "config.site"),
            })
        if self.conanfile.settings.compiler in ("gcc", "clang"):
            if self.arch == "x86":
                # fix finding PLATFORM_TRIPLET (used for e.g. extensions of native python modules)
                env_vars["CPPFLAGS"] = "-m32"

        with tools.environment_append(env_vars):
            autotools.configure(configure_dir=os.path.join(self.conanfile.source_folder, self.conanfile._source_subfolder), args=args)
            autotools.make()

    def build_msvc(self):
        with tools.chdir(os.path.join(self.conanfile._source_subfolder, "PCBuild")):
            build_type = self.build_type
            arch = "x64" if self.arch == "x86_64" else "Win32"
        self.conanfile.run("build.bat -c {build_type} -p {arch}".format(build_type=build_type, arch=arch))

    def package(self):
        if self.conanfile.settings.compiler == "Visual Studio":
            pass
        else:
            with tools.chdir(self.conanfile.build_folder):
                autotools = AutoToolsBuildEnvironment(self.conanfile)
                autotools.make(args=["install", "-j1"])
                shutil.rmtree(os.path.join(self.conanfile.package_folder, "lib", "pkgconfig"))

        cpython_symlink = os.path.join(self.conanfile.package_folder, "bin", "python")
        if self.os == "Windows":
            cpython_symlink += ".exe"
        if not os.path.exists(cpython_symlink):
            self.conanfile.output.info("Creating symbolic link: {}".format(cpython_symlink))
            os.symlink("python{}".format(self.version_major_minor), cpython_symlink)

        self.conanfile.copy("LICENSE", src=os.path.join(self.conanfile.source_folder, self.conanfile._source_subfolder), dst="licenses")
        self.conanfile.copy("LICENSE.md", dst="licenses")
