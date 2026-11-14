# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage

from spack.package import *

class M3dc1(CMakePackage, CudaPackage):
    """M3D-C1: a scalable code for 3D extended MHD simulation of
    tokamak plasmas."""

    homepage = "https://m3dc1.pppl.gov"
    git = "https://github.com/PrincetonUniversity/M3DC1.git"

    maintainers("jacobmerson")

    # With a Kokkos +wrapper dependency, the MPI C++ wrapper calls nvcc_wrapper,
    # which links with the real host compiler rather than Spack's compiler
    # wrapper, so injected flags never reach C++ links. Pass them through CMake.
    flag_handler = build_system_flags

    version("master", branch="master")

    # ------------------------------------------------------------------
    # Variants mirroring the -D flags in your cmake invocation
    # ------------------------------------------------------------------
    variant("pspline", default=False, description="Enable PSPLINE support")
    variant("3d", default=False, description="Enable 3D support")
    variant("trilinos", default=False, description="Enable Trilinos support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("complex", default=False, description="Enable complex arithmetic")
    variant("particle", default=False, description="Enable particle support")
    variant("gpu", default=False, description="Enable GPU support")
    variant("st", default=False, description="Enable ST support")
    variant("adas", default=False, description="Enable ADAS support")

    # ------------------------------------------------------------------
    # Build dependencies
    # ------------------------------------------------------------------
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build")

    depends_on("mpi", type=("build", "link", "run"))

    depends_on("gsl", type=("build", "link"))
    depends_on("fftw", type=("build", "link"))
    depends_on("lapack", type=("build", "link"))
    depends_on("hdf5+fortran+hl+mpi", type=("build", "link"))
    depends_on("petsc+mumps+superlu-dist", type=("build", "link"))
    depends_on("petsc~complex", when="~complex", type=("build", "link"))
    depends_on("petsc+complex", when="+complex", type=("build", "link"))
    depends_on("zoltan+parmetis~fortran", type=("build", "link"))
    depends_on("pumi@2.2.8:+zoltan", type=("build", "link"))
    # The stellarator version reads VMEC equilibria through NetCDF.
    depends_on("netcdf-c+mpi", when="+st", type=("build", "link"))
    depends_on("pspline", when="+pspline", type=("build", "link"))
    depends_on("cuda", when="+gpu", type=("build", "link"))

    def cmake_args(self):
        spec = self.spec

        args = [
            self.define("CMAKE_C_COMPILER", spec["mpi"].mpicc),
            self.define("CMAKE_CXX_COMPILER", spec["mpi"].mpicxx),
            self.define("CMAKE_Fortran_COMPILER", spec["mpi"].mpifc),
            self.define_from_variant("M3DC1_ENABLE_PSPLINE", "pspline"),
            self.define_from_variant("M3DC1_ENABLE_3D", "3d"),
            self.define_from_variant("M3DC1_ENABLE_TRILINOS", "trilinos"),
            self.define_from_variant("M3DC1_ENABLE_OPENMP", "openmp"),
            self.define_from_variant("M3DC1_ENABLE_COMPLEX", "complex"),
            self.define_from_variant("M3DC1_ENABLE_PARTICLE", "particle"),
            self.define_from_variant("M3DC1_ENABLE_GPU", "gpu"),
            self.define_from_variant("M3DC1_ENABLE_ST", "st"),
            self.define_from_variant("M3DC1_ENABLE_ADAS", "adas"),
        ]

        if "+st" in spec:
            args.append(self.define("NetCDF_ROOT", spec["netcdf-c"].prefix))

        if "+pspline" in spec:
            pspline_prefix = spec["pspline"].prefix
            args += [
                self.define("PSPLINE_ROOT", pspline_prefix),
                self.define("PSPLINE_INCLUDE_DIR", pspline_prefix.include),
                self.define(
                    "PSPLINE_LIBRARY",
                    join_path(pspline_prefix.lib, "libpspline.a"),
                ),
            ]
        
        if "+openmp" in spec:
            openmp_flag = self.compiler.openmp_flag
            args.append(self.define("OpenMP_Fortran_FLAGS", openmp_flag))

        return args
    
    def install(self, spec, prefix):
        mkdirp(prefix.bin)

        exe_name = "m3dc1"

        if "+3d" in spec:
            exe_name += "_3d"
        else:
            exe_name += "_2d"

        if "+trilinos" in spec:
            exe_name += "_trilinos"

        if "+complex" in spec:
            exe_name += "_complex"

        if "+openmp" in spec:
            exe_name += "_omp"

        if "+st" in spec:
            exe_name += "_st"

        if "+particle" in spec:
            exe_name += "_pic"

        executables = [
            join_path(self.build_directory, "unstructured", exe_name),
            join_path(self.build_directory, "m3dc1_scorec", "create_smb"),
            join_path(self.build_directory, "m3dc1_scorec", "split_smb"),
            join_path(self.build_directory, "m3dc1_scorec", "check_smb"),
            join_path(self.build_directory, "m3dc1_scorec", "show_meshcount"),
            join_path(self.build_directory, "m3dc1_scorec", "vtk_order"),
        ]

        for exe in executables:
            install(exe, prefix.bin)

        # The OpenADAS ADF11 data is downloaded into the build directory, and
        # the adas_adf11 input has no default. Install it so the path below
        # stays valid after the build directory is gone.
        if "+adas" in spec:
            install_tree(
                join_path(self.build_directory, "adas", "adf11"),
                join_path(prefix.share, "m3dc1", "adas", "adf11"),
            )

    def setup_run_environment(self, env):
        # Value for the adas_adf11 input in C1input.
        if self.spec.satisfies("+adas"):
            env.set(
                "M3DC1_ADAS_ADF11", join_path(self.prefix.share, "m3dc1", "adas", "adf11")
            )
