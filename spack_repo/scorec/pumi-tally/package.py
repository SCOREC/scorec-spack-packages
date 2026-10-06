# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack.package import *


class PumiTally(CMakePackage, CudaPackage):
    homepage      = "https://github.com/Fuad-HH/PumiTally"
    git      = "https://github.com/Fuad-HH/PumiTally.git"
    maintainers = ["Fuad-HH"]

    version("main", branch="main")
    version("openmc", branch="main")

    variant("pic", default=False, description="Build with position independent code (-fPIC)")
    variant("shared", default=True, description="Build as shared library")

    conflicts("+pic", when="+shared")
    conflicts("+shared", when="+pic")

    depends_on('mpi')
    depends_on("cxx", type="build")
    depends_on("c", type="build")
    depends_on("cmake", type="build")

    depends_on("pumi-pic@pumitally")
    conflicts(
        "^pumi-pic~pic~shared",
        when="+shared",
        msg="PUMI-Tally builds shared or links into shared consumers; PUMI-PiC must be built with +pic or +shared",
    )
    conflicts(
        "^pumi-pic~pic~shared",
        when="+pic",
        msg="PUMI-Tally builds shared or links into shared consumers; PUMI-PiC must be built with +pic or +shared",
    )

    def setup_build_environment(self, env):
        # Same problem PUMI-PiC has: Kokkos' launch compiler swaps the compiler
        # for nvcc_wrapper on every translation unit that depends on Kokkos, and
        # nvcc_wrapper's default g++ host compiler knows nothing about MPI.
        # FindMPI adds no include directory of its own because CMAKE_CXX_COMPILER
        # is already mpicxx, so <mpi.h> (pulled in here via Omega_h_mpi.h) goes
        # missing.  Point nvcc_wrapper at the same MPI wrapper we hand to CMake.
        # Note: this applies to kokkos~wrapper too -- Kokkos still installs
        # kokkos_launch_compiler and enables it globally whenever it is +cuda.
        if self.spec.satisfies("^kokkos+cuda"):
            env.set("NVCC_WRAPPER_DEFAULT_COMPILER", self.spec["mpi"].mpicxx)

    def cmake_args(self):
        args = []
        args.append("-DCMAKE_CXX_COMPILER:FILEPATH={0}".format(self.spec["mpi"].mpicxx))
        args.append("-DCMAKE_C_COMPILER:FILEPATH={0}".format(self.spec["mpi"].mpicc))
        args.append("-DPUMITALLYOPENMC_ENABLE_TESTS=OFF")
        if "+shared" in self.spec:
            args.append("-DBUILD_SHARED_LIBS=ON")
        elif "+pic" in self.spec:
            args.append("-DCMAKE_POSITION_INDEPENDENT_CODE=ON")
        return args


