# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration, ConanException
from conans.tools import detected_architecture, get_env
from conans.client.tools.oss import detected_os
import os
import shutil


class CPythonBaseConanFile(ConanFile):
    _base_name = "cpython"
    version = "3.7.3"
    description = "The Python programming language"
    topics = ("conan", "python", "programming", "language", "scripting")
    url = "https://github.com/bincrafters/conan-cpython"
    homepage = "https://www.python.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Python-2.0"

    exports = ()
    exports_sources = ("../config.site", "../LICENSE.md", )

    _base_options = {
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
        # "curses": [True, False],  # FIXME: add curses readline
        "ipv6": [True, False],
    }
    _base_default_options = {
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
        # "curses": True,
        "ipv6": True,
    }

    _source_subfolder = "source_subfolder"

    @property
    def _version_major_minor(self):
        return ".".join(self.version.split(".")[:2])

    @property
    def _cross_compiling(self):
        return self._os != detected_os() or self._arch != detected_architecture()

    @property
    def _cpython_for_regen(self):
        if self._is_installer:
            raise ConanException("installer cannot be cross built: no python executable for regen available")
        else:
            return self.deps_user_info["cpython_installer"].CPYTHON_BIN

    def configure(self):
        del self.settings.compiler.libcxx
        if self._is_installer:
            if self._cross_compiling:
                raise ConanInvalidConfiguration("installer cannot be cross built")
        else:
            if self.options.shared:
                del self.options.fPIC
            if self._os in ("Windows", "Macos"):
                del self.options.nis

    def config_options(self):
        if not self._is_installer:
            if "readline" in self.options:
                self.options["readline"].shared = True

    def requirements(self):
        self.requires("OpenSSL/1.1.1c@conan/stable", private=self._is_installer)
        if self._options("bz2"):
            self.requires("bzip2/1.0.6@conan/stable", private=self._is_installer)
        if self._options("ctypes"):
            self.requires("libffi/3.2.1@bincrafters/stable", private=self._is_installer)
        if self._options("dbm"):
            self.requires("libdb/5.3.28@bincrafters/stable", private=self._is_installer)  # FIXME: submit to bincrafters
        if self._options("decimal"):
            self.requires("mpdecimal/2.4.2@bincrafters/stable", private=self._is_installer)  # FIXME: submit to bincrafters
        if self._options("expat"):
            self.requires("Expat/2.2.6@pix4d/stable", private=self._is_installer)
        if self._options("gdbm"):
            self.requires("gdbm/1.18.1@bincrafters/stable", private=self._is_installer)
        if self._options("lzma"):
            self.requires("lzma/5.2.4@bincrafters/stable", private=self._is_installer)
        if self._options("nis"):
            self.requires("libnsl/1.2.0@bincrafters/stable", private=self._is_installer)  # FIXME: submit to bincrafters
        if self._options("sqlite3"):
            self.requires("sqlite3/3.28.0@bincrafters/stable", private=self._is_installer)
        if self._options("tkinter"):
            self.requires("tk/8.6.9.1@bincrafters/stable", private=self._is_installer)  # FIXME: submit to bincrafters
        if self._options("uuid"):
            self.requires("libuuid/1.0.3@bincrafters/stable", private=self._is_installer)
        # if self._options("curses"):  # FIXME: add curses
        #     self.requires("ncurses/6.1@conan/stable", private=self._is_installer)

    def build_requirements(self):
        if self._is_installer and self._cross_compiling:
            self.build_requires("cpython_installer/{}@{}/{}".format(self.version, self.user, self.channel))

    def source(self):
        filename = "Python-{}.tgz".format(self.version)
        url = "https://www.python.org/ftp/python/{}/{}".format(self.version, filename)
        sha256 = "d62e3015f2f89c970ac52343976b406694931742fbde2fed8d1ce8ebb4e1f8ff"

        tools.get(url, sha256=sha256)
        os.rename("Python-{}".format(self.version), self._source_subfolder)

    def _fix_source(self):
        # fix library name of mpdecimal
        tools.replace_in_file(os.path.join(self._source_subfolder, "setup.py"),
                              ":libmpdec.so.2", "libmpdec")
        tools.replace_in_file(os.path.join(self._source_subfolder, "setup.py"),
                              "libraries = ['libmpdec']", "libraries = ['mpdec']")

        makefile = os.path.join(self._source_subfolder, "Makefile.pre.in")
        tools.replace_in_file(makefile,
                              "@OPT@",
                              "@OPT@ @CFLAGS@")

    def build(self):
        self._fix_source()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def _build_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.target = autotools.host

        if self._options("uuid"):
            autotools.include_paths += ["{}/uuid".format(d) for d in self.deps_cpp_info["libuuid"].includedirs]
        args = [
            "--enable-shared" if self._options("shared") else "--disable-shared",
            "--with-gcc", "--without-icc",
            "--with-system-expat" if self._options("expat") else "--without-system-expat",
            "--with-system-libmpdec" if self._options("decimal") else "--without-system-libmpdec",
            "--enable-optimizations" if self._options("optimizations") else "--disable-optimizations",
            "--with-lto" if self._options("lto") else "--without-lto",
            "--enable-ipv6" if self._options("ipv6") else "--disable-ipv6",
            "--with-openssl={}".format(self.deps_cpp_info["OpenSSL"].rootpath),
        ]
        if self._build_type == "Debug":
            args.extend(["--with-pydebug", "--with-assertions"])
        else:
            args.extend(["--without-pydebug", "--without-assertions"])
        if self._options("tkinter"):
            tcltk_includes = []
            tcltk_libs = []
            for dep in ("tcl", "tk", "zlib"):
                tcltk_includes += ["-I{}".format(d) for d in self.deps_cpp_info[dep].includedirs]
                tcltk_libs += ["-l{}".format(lib) for lib in self.deps_cpp_info[dep].libs]
            args.extend([
                "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
                "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
            ])
        env_vars = {
            "PKG_CONFIG": os.path.abspath("pkg-config"),
        }
        if self._cross_compiling:
            env_vars.update({
                "PYTHON_FOR_REGEN": self._cpython_for_regen,
                "CONFIG_SITE": "config.site",
            })
        if self.settings.compiler in ("gcc", "clang"):
            if self._arch == "x86":
                # fix finding PLATFORM_TRIPLET (used for e.g. extensions of native python modules)
                env_vars["CPPFLAGS"] = "-m32"

        with tools.environment_append(env_vars):
            autotools.configure(configure_dir=self._source_subfolder, args=args)
            autotools.make()

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder, "PCBuild")):
            arch = "x64" if self._arch == "x86_64" else "Win32"
            self.run("build.bat -c {build_type} -p {arch}".format(build_type=self._build_type, arch=arch))

    def package(self):
        if self.settings.compiler == "Visual Studio":
            pass
        else:
            with tools.chdir(self.build_folder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make(args=["install", "-j1"])
                shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))

        cpython_symlink = os.path.join(self.package_folder, "bin", "python")
        if self._os == "Windows":
            cpython_symlink += ".exe"
        if not os.path.exists(cpython_symlink):
            self.output.info("Creating symbolic link: {}".format(cpython_symlink))
            os.symlink("python{}".format(self._version_major_minor), cpython_symlink)

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
