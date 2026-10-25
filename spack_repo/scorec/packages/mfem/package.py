# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack_repo.builtin.build_systems import cmake
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.packages.mfem.package import Mfem as BuiltinMfem

from spack.package import *


class Mfem(BuiltinMfem, CMakePackage):
    """Builtin mfem plus a CMake build, which installs the MFEMConfig.cmake that
    CMake projects such as pcms consume with find_package(MFEM).

    From https://github.com/spack/spack-packages/pull/143; drop once merged.
    build_system=generic is the builtin recipe unchanged.
    """

    build_system("generic", "cmake", default="generic")
    # The CMake build is supported in spack starting with mfem v4.9.0
    # See comment from v-dobrev https://github.com/spack/spack-packages/pull/143
    conflicts("build_system=cmake", when="@:4.8")
    # CMake only handles one build mode at a time
    conflicts("+shared+static", when="build_system=cmake")
    # The CMake build has build_type instead
    conflicts("+debug", when="build_system=cmake", msg="use build_type=Debug")

    # Even with CMake, the C compiler is only needed in some configurations.
    depends_on("c", type="build", when="build_system=cmake")
    depends_on("fortran", type="build", when="+mumps build_system=cmake")


def str_to_timerid(timer_type):
    timer_ids = {"auto": "-1", "std": "0", "posix": "2", "mac": "4", "mpi": "6"}
    return timer_ids[timer_type]


class CMakeBuilder(cmake.CMakeBuilder):
    # An explicit builder does not run the builtin package's make-based
    # run_after callbacks, so cache the test sources here instead.
    @run_after("install")
    def cache_test_sources(self):
        """Copy the example source files after the package is installed to an
        install test subdirectory for use during `spack test run`."""
        extra_install_tests = [self.pkg.examples_src_dir, self.pkg.examples_data_dir]
        cache_extra_test_sources(self.pkg, extra_install_tests)

    def cmake_args(self):
        args = [
            self.define_from_variant("MFEM_USE_MPI", "mpi"),
            self.define_from_variant("MFEM_USE_METIS", "metis"),
            self.define_from_variant("MFEM_USE_OPENMP", "openmp"),
            self.define_from_variant("MFEM_USE_OCCA", "occa"),
            self.define_from_variant("MFEM_USE_RAJA", "raja"),
            self.define_from_variant("MFEM_USE_CEED", "libceed"),
            self.define_from_variant("MFEM_USE_UMPIRE", "umpire"),
            self.define_from_variant("MFEM_USE_AMGX", "amgx"),
            self.define_from_variant("MFEM_THREAD_SAFE", "threadsafe"),
            self.define_from_variant("MFEM_USE_SUPERLU", "superlu-dist"),
            self.define_from_variant("MFEM_USE_STRUMPACK", "strumpack"),
            self.define_from_variant("MFEM_USE_SUITESPARSE", "suite-sparse"),
            self.define_from_variant("MFEM_USE_PETSC", "petsc"),
            self.define_from_variant("MFEM_USE_MUMPS", "mumps"),
            self.define_from_variant("MFEM_USE_SLEPC", "slepc"),
            self.define_from_variant("MFEM_USE_SUNDIALS", "sundials"),
            self.define_from_variant("MFEM_USE_PUMI", "pumi"),
            self.define_from_variant("MFEM_USE_GSLIB", "gslib"),
            self.define_from_variant("MFEM_USE_MPFR", "mpfr"),
            self.define_from_variant("MFEM_USE_LAPACK", "lapack"),
            self.define_from_variant("MFEM_USE_NETCDF", "netcdf"),
            self.define_from_variant("MFEM_USE_CONDUIT", "conduit"),
            self.define_from_variant("MFEM_USE_ZLIB", "zlib"),
            self.define_from_variant("MFEM_USE_GNUTLS", "gnutls"),
            self.define_from_variant("MFEM_USE_LIBUNWIND", "libunwind"),
            self.define_from_variant("MFEM_USE_FMS", "fms"),
            self.define_from_variant("MFEM_USE_GINKGO", "ginkgo"),
            self.define_from_variant("MFEM_USE_HIOP", "hiop"),
            self.define_from_variant("MFEM_USE_CUDA", "cuda"),
            self.define_from_variant("MFEM_USE_HIP", "rocm"),
            self.define_from_variant("MFEM_USE_ENZYME", "enzyme"),
            self.define_from_variant("MFEM_ENABLE_EXAMPLES", "examples"),
            self.define_from_variant("MFEM_ENABLE_MINIAPPS", "miniapps"),
            self.define_from_variant("MFEM_USE_EXCEPTIONS", "exceptions"),
            self.define_from_variant("MFEM_PRECISION", "precision"),
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define("MFEM_ENABLE_TESTING", True),
        ]
        if self.spec.satisfies("@4.10:"):
            args.append(self.define_from_variant("MFEM_USE_CUDSS", "cudss"))

        # CMakeBuilder.std_args() does not forward cuda_arch or amdgpu_target
        if self.spec.satisfies("+cuda"):
            args.append(self.define_cuda_architectures(self.pkg))
        if self.spec.satisfies("+rocm"):
            args.append(self.define_hip_architectures(self.pkg))

        cxxstd = self.spec.variants["cxxstd"].value
        if cxxstd != "auto":
            args.append(self.define_from_variant("CMAKE_CXX_STANDARD", "cxxstd"))

        timer = self.spec.variants["timer"].value
        if timer != "auto":
            args.append(self.define("MFEM_TIMER_TYPE", str_to_timerid(timer)))

        if self.spec.satisfies("+petsc"):
            args.append(self.define("PETSC_DIR", self.spec["petsc"].prefix))
            args.append(self.define("PETSC_ARCH", ""))

        if self.spec.satisfies("+mumps"):
            args.append(self.define("MUMPS_REQUIRED_PACKAGES", ""))

        if self.spec.satisfies("+strumpack"):
            args.append(self.define("STRUMPACK_REQUIRED_PACKAGES", "MPI"))

        if self.spec.satisfies("+netcdf"):
            args.append(self.define("NetCDF_REQUIRED_PACKAGES", ""))

        if self.spec.satisfies("+pumi"):
            args.append(self.define("PUMI_DIR", self.spec["pumi"].prefix))

        if self.spec.satisfies("+mpfr"):
            mpfr = self.spec["mpfr"]
            args.append(self.define("MPFR_INCLUDE_DIRS", mpfr.headers.directories))
            args.append(self.define("MPFR_LIBRARIES", mpfr.libs.libraries))
            args.append(self.define("MPFR_FOUND", True))

        return args
