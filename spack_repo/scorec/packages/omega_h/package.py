# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack_repo.builtin.packages.omega_h.package import OmegaH as BuiltinOmegaH

from spack.package import *


class OmegaH(BuiltinOmegaH):
    """Builtin omega-h plus fixes SCOREC needs that aren't upstream yet."""

    # First version with https://github.com/SCOREC/omega_h/pull/235 (pybind11
    # as a private dependency). TODO: link spack-packages PR adding it.
    version(
        "11.4.0-scorec",
        commit="8fc0a0bb3140e601cea86ebcbd2faecd30b410bf",
        git="https://github.com/SCOREC/omega_h.git",
    )

    # https://github.com/SCOREC/omega_h/pull/246 . Drop patch when that merges.
    patch("r3d-few-strict-aliasing.patch", when="@11.0.0-scorec:11.4.0-scorec")
