# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack_repo.builtin.packages.omega_h.package import OmegaH as BuiltinOmegaH

from spack.package import *


class OmegaH(BuiltinOmegaH):
    """Builtin omega-h plus fixes SCOREC needs that aren't upstream yet."""

    version(
        "11.4.0-scorec",
        commit="8e8bd32ab6aab8555a2c749f8beebbd48b89c320",
        git="https://github.com/SCOREC/omega_h.git",
    )

    depends_on("cuda", type="build", when="+kokkos ^kokkos+cuda")
    depends_on("hip", type="build", when="+kokkos ^kokkos+rocm")

    patch("omega_h-export-dependency-dirs.patch", when="@11.4.0-scorec")

    def cmake_args(self):
        args = super().cmake_args()
        if self.spec.satisfies("@11.4.0-scorec+python"):
            args.append(self.define("PyOmega_h_DEST", python_platlib))
        return args + self.kokkos_cxx_args()

    def kokkos_cxx_args(self):
        spec = self.spec
        if spec.satisfies("+kokkos ^kokkos+rocm") and not (
            spec.satisfies("^kokkos %cxx=clang") or spec.satisfies("^kokkos %cxx=rocmcc")
        ):
            return [self.define("CMAKE_CXX_COMPILER", spec["hip"].hipcc)]
        return []
