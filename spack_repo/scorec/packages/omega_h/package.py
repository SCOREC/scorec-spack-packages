# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack_repo.builtin.packages.omega_h.package import OmegaH as BuiltinOmegaH

from spack.package import *


class OmegaH(BuiltinOmegaH):
    """Builtin omega-h plus fixes SCOREC needs that aren't upstream yet."""

    # First version with https://github.com/SCOREC/omega_h/pull/235 (pybind11
    # as a private dependency) and https://github.com/SCOREC/omega_h/pull/198
    # (r3d::Few strict-aliasing fix). TODO: link spack-packages PR adding it.
    version(
        "11.4.0-scorec",
        commit="07ec34ba8fddd416b41db77c1e4a97bb0e256e69",
        git="https://github.com/SCOREC/omega_h.git",
    )

    # Omega_h follows Kokkos's backend, but with kokkos+cuda it compiles through
    # kokkos's nvcc_wrapper, which needs nvcc on PATH.
    depends_on("cuda", type="build", when="+kokkos ^kokkos+cuda")
    # With kokkos+rocm it compiles with hipcc.
    depends_on("hip", type="build", when="+kokkos ^kokkos+rocm")

    # Make PyOmega_h_DEST overridable (default lib/, not lib64/) so the python
    # module lands in spack's python_platlib. Drop once merged upstream.
    patch("pyomega_h-install-location.patch", when="@11.4.0-scorec+python")

    def cmake_args(self):
        args = super().cmake_args()
        if self.spec.satisfies("@11.4.0-scorec+python"):
            args.append(self.define("PyOmega_h_DEST", python_platlib))
        return args + self.kokkos_cxx_args()

    def kokkos_cxx_args(self):
        # Kokkos's HIP backend needs its users compiled with hipcc unless Kokkos
        # itself was built with an AMD-capable Clang. Following approach from:
        # builtin kokkos-kernels, cmake_args.
        spec = self.spec
        if spec.satisfies("+kokkos ^kokkos+rocm") and not (
            spec.satisfies("^kokkos %cxx=clang") or spec.satisfies("^kokkos %cxx=rocmcc")
        ):
            return [self.define("CMAKE_CXX_COMPILER", spec["hip"].hipcc)]
        return []
