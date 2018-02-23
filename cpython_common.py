# -*- coding: utf-8 -*-

from conans import AutoToolsBuildEnvironment, tools
from conans.util.env_reader import get_env
import os
import shutil
import tempfile


def cpython_is_mingw(conanfile):
    return conanfile._os() == "Windows" and conanfile.settings.compiler == "gcc"


def cpython_major_minor(conanfile):
    return ".".join(conanfile.version.split(".")[:2])


def cpython_options():
    return {  # FIXME: add curses readline
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
        "tcltk": [True, False],
        "uuid": [True, False],
        "ipv6": [True, False],
    }


def cpython_default_options():
    return {
        "shared": False,
        "fPIC": True,
        "optimizations": False,
        "lto": False,
        "ipv6": True,
        "bz2": True,
        "ctypes": True,
        "dbm": True,
        "decimal": True,
        "expat": True,
        "gdbm": True,
        "lzma": True,
        "nis": True,
        "sqlite3": True,
        "tcltk": True,
        "uuid": True,
    }


def cpython_configure(conanfile):
    if hasattr(conanfile.settings.compiler, "libcxx"):
        del conanfile.settings.compiler.libcxx


def cpython_config_options(conanfile):
    if conanfile.options.shared:
        del conanfile.options.fPIC
    if conanfile._os() in ("Windows", "Macos"):
        del conanfile.options.nis


def cpython_get_requirements(conanfile):
    reqs = []
    reqs.append("OpenSSL/1.1.1a@conan/stable")
    if conanfile.options.bz2:
        reqs.append("bzip2/1.0.6@conan/stable")
    if conanfile.options.ctypes:
        reqs.append("libffi/3.3-rc0@maarten/testing")  # FIXME: submit to bincrafters
    if conanfile.options.dbm:
        reqs.append("libdb/5.3.28@maarten/testing")  # FIXME: submit to bincrafters
    if conanfile.options.decimal:
        reqs.append("mpdecimal/2.4.2@maarten/testing")  # FIXME: submit to bincrafters
    if conanfile.options.expat:
        reqs.append("expat/2.2.5@bincrafters/stable")
    if conanfile.options.gdbm:
        reqs.append("gdbm/1.18.1@maarten/testing")  # FIXME: submit to bincrafters
    if conanfile.options.lzma:
        reqs.append("lzma/5.2.3@bincrafters/stable")
    if conanfile.options.nis:
        reqs.append("libnsl/1.2.0@maarten/testing")  # FIXME: submit to bincrafters
    if conanfile.options.sqlite3:
        reqs.append("sqlite3/3.25.3@bincrafters/stable")
    if conanfile.options.tcltk:
        reqs.append("tcl/8.6.9@maarten/testing")
        reqs.append("tk/8.6.9@maarten/testing")  # FIXME: submit to bincrafters
    if conanfile.options.uuid:
        reqs.append("libuuid/1.0.3@bincrafters/stable")
    return reqs


def cpython_source(conanfile):
    filename = "Python-{}.tgz".format(conanfile.version)
    url = "https://www.python.org/ftp/python/{}/{}".format(conanfile.version, filename)
    sha256 = "f09d83c773b9cc72421abba2c317e4e6e05d919f9bcf34468e192b6a6c8e328d"

    dlfilepath = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(dlfilepath) and not get_env("CPYTHON_FORCE_DOWNLOAD", False):
        conanfile.output.info("Skipping download. Using cached {}".format(dlfilepath))
    else:
        tools.download(url, dlfilepath)
    tools.check_sha256(dlfilepath, sha256)
    tools.untargz(dlfilepath)
    os.rename("Python-{}".format(conanfile.version), conanfile._source_subfolder)

    # fix library name of mpdecimal
    tools.replace_in_file(os.path.join(conanfile.source_folder, conanfile._source_subfolder, "setup.py"),
                          ":libmpdec.so.2", "libmpdec")
    tools.replace_in_file(os.path.join(conanfile.source_folder, conanfile._source_subfolder, "setup.py"),
                          "libraries = ['libmpdec']", "libraries = ['mpdec']")

    # on building x86 python on x86_64: readlink is just fine
    tools.replace_in_file(os.path.join(conanfile.source_folder, conanfile._source_subfolder, "configure"),
                          "as_fn_error $? \"readelf for the host is required for cross builds\"",
                          "# as_fn_error $? \"readelf for the host is required for cross builds\"")

    makefile = os.path.join(conanfile.source_folder, conanfile._source_subfolder, "Makefile.pre.in")
    tools.replace_in_file(makefile,
                          "@OPT@",
                          "@OPT@ @CFLAGS@")


def cpython_build(conanfile):
    if conanfile.settings.compiler == "Visual Studio":
        cpython_build_msvc(conanfile)
    else:
        cpython_build_autotools(conanfile)


def cpython_build_autotools(conanfile):
    autotools = AutoToolsBuildEnvironment(conanfile)
    autotools.target = autotools.host

    if conanfile.options.uuid:
        autotools.include_paths += ["{}/uuid".format(d) for d in conanfile.deps_cpp_info["libuuid"].includedirs]
    args = [
        "--enable-shared" if conanfile.options.shared else "--disable-shared",
        "--with-gcc", "--without-icc",
        "--with-system-expat" if conanfile.options.expat else "--without-system-expat",
        "--with-system-libmpdec" if conanfile.options.decimal else "--without-system-libmpdec",
        "--enable-optimizations" if conanfile.options.optimizations else "--disable-optimizations",
        "--with-lto" if conanfile.options.lto else "--without-lto",
        "--with-openssl={}".format(conanfile.deps_cpp_info["OpenSSL"].rootpath),
    ]
    if conanfile._build_type() == "Debug":
        args.extend(["--with-pydebug", "--with-assertions"])
    else:
        args.extend(["--without-pydebug", "--without-assertions"])
    if conanfile.options.tcltk:
        tcltk_includes = []
        tcltk_libs = []
        for dep in ("tcl", "tk", "zlib"):
            tcltk_includes += ["-I{}".format(d) for d in conanfile.deps_cpp_info[dep].includedirs]
            tcltk_libs += ["-l{}".format(lib) for lib in conanfile.deps_cpp_info[dep].libs]
        args.extend([
            "--with-tcltk-includes={}".format(" ".join(tcltk_includes)),
            "--with-tcltk-libs={}".format(" ".join(tcltk_libs)),
        ])
    args.append("--enable-ipv6" if conanfile.options.ipv6 else "--disable-ipv6")
    env_vars = {
        "PKG_CONFIG": os.path.abspath("pkg-config"),
    }
    if conanfile._is_crosscompile():
        env_vars.update({
            "PYTHON_FOR_REGEN": conanfile._python_regen(),
            "CONFIG_SITE": os.path.join(conanfile.source_folder, "config.site"),
        })
    if conanfile.settings.compiler in ("gcc", "clang"):
        if conanfile._arch() == "x86":
            # fix finding PLATFORM_TRIPLET (used for e.g. extensions of native python modules)
            env_vars["CPPFLAGS"] = "-m32"

    with tools.environment_append(env_vars):
        autotools.configure(configure_dir=os.path.join(conanfile.source_folder, conanfile._source_subfolder), args=args)
        autotools.make()


def cpython_build_msvc(conanfile):
    with tools.chdir(os.path.join(conanfile._source_subfolder, "PCBuild")):
        build_type = conanfile._build_type()
        arch = "x64" if conanfile._arch() == "x86_64" else "Win32"
        conanfile.run("build.bat -c {build_type} -p {arch}".format(build_type=build_type, arch=arch))


def cpython_package(conanfile):
    if conanfile.settings.compiler == "Visual Studio":
        pass
    else:
        with tools.chdir(conanfile.build_folder):
            autotools = AutoToolsBuildEnvironment(conanfile)
            autotools.make(args=["install", "-j1"])
            shutil.rmtree(os.path.join(conanfile.package_folder, "lib", "pkgconfig"))

    cpython_symlink = os.path.join(conanfile.package_folder, "bin", "python")
    if conanfile._os() == "Windows":
        cpython_symlink += ".exe"
    if not os.path.exists(cpython_symlink):
        conanfile.output.info("Creating symbolic link: {}".format(cpython_symlink))
        os.symlink("python{}".format(cpython_major_minor(conanfile)), cpython_symlink)

    conanfile.copy("LICENSE", src=os.path.join(conanfile.source_folder, conanfile._source_subfolder), dst="licenses")
