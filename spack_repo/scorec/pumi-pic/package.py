# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack.package import *


class PumiPic(CMakePackage, CudaPackage):
    homepage      = "https://github.com/SCOREC/pumi-pic"
    git      = "https://github.com/SCOREC/pumi-pic"
    maintainers = ['Angelyr','jacobmerson','cwsmith']

    version("master", branch="master")
    version('2.1.4', commit='b6678b0a0b8c9ad1e143831bdc2920b944b0f5ff')
    version('2.1.3', commit='8130075d05f063413b8f637bcd9444a108e31f5b')
    version(
            'pumitally',
            git="https://github.com/Fuad-HH/pumi-pic.git",
            branch='make_search_class'
    )

    variant("cabana", default=True, description="Build with cabana")
    variant("pic", default=False, description="Build with position independent code (-fPIC)")
    variant("shared", default=False, description="Build shared libraries")

    conflicts("+pic", when="+shared")
    conflicts("+shared", when="+pic")

    depends_on('mpi')
    depends_on("cxx", type="build")
    depends_on("c", type="build")
    depends_on("cmake", type="build")

    depends_on("engpar@master")
    conflicts(
        "^engpar~pic~shared",
        when="+shared",
        msg="PUMI-PiC builds shared or links into shared consumers; EnGPar must be built with +pic or +shared",
    )
    conflicts(
        "^engpar~pic~shared",
        when="+pic",
        msg="PUMI-PiC builds shared or links into shared consumers; EnGPar must be built with +pic or +shared",
    )
    
    depends_on("kokkos@4.7.00:4.7.04")
    depends_on("omega-h@11.2.0-scorec +kokkos")
    depends_on("cabana@0.6.1:0.7.0", when="+cabana")

    conflicts(
        "~cabana",
        when="@pumitally",
        msg="PUMI-Tally requires cabana support."
    )

    # PUMI-PiC and Omega_h get their CUDA support from the Kokkos backend, so
    # only Kokkos needs the CUDA settings propagated to it.  Cabana is the
    # exception: its CMakeLists runs kokkos_check(OPTIONS CUDA_LAMBDA) whenever
    # the Kokkos it finds has the CUDA backend enabled, and only cabana+cuda
    # pulls in kokkos+cuda_lambda.  Key Cabana off the Kokkos we build against
    # (not off pumi-pic's own +cuda) so that specs such as `^kokkos+cuda
    # cuda_arch=120` give a consistent DAG instead of a non-CUDA Cabana linked
    # against a CUDA Kokkos.
    for arch in CudaPackage.cuda_arch_values:
        cuda_dep = "+cuda cuda_arch={0}".format(arch)
        depends_on("kokkos {0}".format(cuda_dep), when=cuda_dep)
        depends_on("cabana {0}".format(cuda_dep), when="+cabana ^kokkos {0}".format(cuda_dep))

    def setup_build_environment(self, env):
        # Kokkos' launch compiler swaps the compiler for nvcc_wrapper on every
        # translation unit that depends on Kokkos.  nvcc_wrapper defaults to a
        # plain g++ host compiler, which loses the MPI wrapper's flags: because
        # CMAKE_CXX_COMPILER is already mpicxx, FindMPI reports that no extra
        # flags are needed and MPI::MPI_CXX carries no include directory, so
        # <mpi.h> goes missing.  Point nvcc_wrapper at the same MPI wrapper we
        # hand to CMake below.
        # Note: this applies to kokkos~wrapper too -- Kokkos still installs
        # kokkos_launch_compiler and enables it globally whenever it is +cuda.
        if self.spec.satisfies("^kokkos+cuda"):
            env.set("NVCC_WRAPPER_DEFAULT_COMPILER", self.spec["mpi"].mpicxx)

    def cmake_args(self):
        args = []
        args.append("-DCMAKE_CXX_COMPILER:FILEPATH={0}".format(self.spec["mpi"].mpicxx))
        args.append("-DCMAKE_C_COMPILER:FILEPATH={0}".format(self.spec["mpi"].mpicc))
        if "+shared" in self.spec:
            args.append("-DBUILD_SHARED_LIBS=ON")
        elif "+pic" in self.spec:
            args.append("-DCMAKE_POSITION_INDEPENDENT_CODE=ON")
        if "+cabana" in self.spec:
            args.append("-DENABLE_CABANA=ON")
        return args


