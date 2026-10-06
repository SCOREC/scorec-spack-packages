# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class OpenmcPumi(CMakePackage):
    """This is a fork of OpenMC (https://github.com/openmc-dev/openmc/) to
    integrate PumiPIC based accelerated tally: Pumi-Tally. It also supports
    DAGMC for CAD geometry and unstructured mesh tally filters.

    OpenMC is a community-developed Monte Carlo neutron and photon transport
    simulation code. It is capable of performing fixed source, k-eigenvalue, and
    subcritical multiplication calculations on models built using either a
    constructive solid geometry or CAD representation. OpenMC supports both
    continuous-energy and multigroup transport. The continuous-energy particle
    interaction data is based on a native HDF5 format that can be generated from ACE
    files produced by NJOY. Parallelism is enabled via a hybrid MPI and OpenMP
    programming model.
    """

    homepage = "https://docs.openmc.org/"
    git = "https://github.com/Fuad-HH/openmc"
    maintainers("Fuad-HH")

    version("main", branch="decouple_pumi_tally", submodules=True)

    variant("openmp", default=True, description="Enable OpenMP support")
    variant("dagmc", default=False, description="Enable DAGMC for CAD geometry and unstructured mesh tally filters")
    variant("pumitally", default=True, description="Enable PUMI-Tally library as tally backend")

    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated

    depends_on("git", type="build")
    # only supporting +mpi since hdf5 is also needed for cabana
    depends_on("hdf5+hl+mpi")
    depends_on("pumi-tally@openmc", when="+pumitally")
    conflicts(
        "^pumi-tally~pic~shared",
        when="+pumitally",
        msg="OpenMC always builds shared libraries; PUMI-Tally must be built with +pic or +shared",
    )
    depends_on("dagmc@develop +openmc", when='+dagmc')

    def setup_build_environment(self, env):
        # When the PUMI-Tally stack is built against kokkos+cuda, the
        # kokkos-nvcc-wrapper package points MPICH_CXX/OMPI_CXX at nvcc_wrapper
        # for every dependent, so mpicxx silently compiles with nvcc. OpenMC is
        # host-only C++ (it only uses the plain PumiTally.h API) and its
        # vendored xtensor does not compile with nvcc's EDG frontend. Pin the
        # MPI wrappers back to the host compiler.
        env.set("MPICH_CC", self.spec["c"].package.cc)
        env.set("MPICH_CXX", self.spec["cxx"].package.cxx)
        env.set("OMPI_CC", self.spec["c"].package.cc)
        env.set("OMPI_CXX", self.spec["cxx"].package.cxx)

    def cmake_args(self):
        options = ["-DCMAKE_INSTALL_LIBDIR=lib"]  # forcing bc sometimes goes to lib64
        options += [self.define_from_variant("OPENMC_USE_PUMITALLY", "pumitally")]

        options += [
            "-DCMAKE_C_COMPILER=%s" % self.spec["mpi"].mpicc,
            "-DCMAKE_CXX_COMPILER=%s" % self.spec["mpi"].mpicxx,
        ]
        options += [self.define("OPENMC_USE_MPI", True)]
        options += [self.define_from_variant("OPENMC_USE_OPENMP", "openmp")]
        options += [self.define_from_variant("OPENMC_USE_DAGMC", "dagmc")]

        return options
