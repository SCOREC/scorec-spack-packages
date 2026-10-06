
# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class Dagmc(CMakePackage):
    """Direct Accelerated Geometry Monte Carlo (DAGMC) Toolkit —
    a toolkit for ray tracing on CAD-based geometries."""

    homepage = "https://svalinn.github.io/DAGMC/"
    git = "https://github.com/svalinn/DAGMC.git"

    version("develop", branch="develop", submodules=True)
    version("3.2.4", tag="v3.2.4", submodules=True)
    version("3.2.3", tag="v3.2.3", submodules=True)
    version("3.2.2", tag="v3.2.2", submodules=True)
    version("3.2.1", tag="v3.2.1", submodules=True)
    version("3.2.0", tag="3.2.0", submodules=True)

    variant("openmc", default=True, description="Build tally libraries for use with OpenMC")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake", type="build")

    depends_on("eigen@:3")
    depends_on("hdf5+hl")
    depends_on("moab@:5.5.0+shared")

    def cmake_args(self):
        args = [
            self.define("MOAB_DIR", self.spec["moab"].prefix),
            self.define_from_variant("BUILD_TALLY", "openmc"),
        ]
        return args
