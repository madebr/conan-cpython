#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bincrafters import build_shared
from conans.util.env_reader import get_env
import os

if __name__ == "__main__":
    build_cpython_installer = get_env("BUILD_CPYTHON_INSTALLER", False)

    if build_cpython_installer:
        subdir = "cpython_installer"
    else:
        subdir = "cpython"

    builder = build_shared.get_builder(
        cwd=os.path.join(os.path.dirname(os.path.realpath(__file__)), subdir),
        docker_entry_script="cd {}".format(subdir)
    )

    if build_cpython_installer:
        arch = get_env("ARCH", None)
        if arch is None:
            raise Exception("cpython_installer does not support cross compilation.")
        builder.add(settings={"arch_build": arch,})
    else:
        builder.add_common_builds()

    builder.run()
