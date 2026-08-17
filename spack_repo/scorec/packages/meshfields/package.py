# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install meshfields
#
# You can edit this file again by typing:
#
#     spack edit meshfields
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class Meshfields(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/SCOREC/meshFields"
    git = "https://github.com/SCOREC/meshFields"

    maintainers("jacobmerson")

    license("BSD-3", checked_by="jacobmerson")

    version('main', branch='main')

    variant('shared', default=False, description='enable shared library builds')

    depends_on('cxx')
    depends_on('cabana', type=('build', 'link', 'run'))
    depends_on('kokkos', type=('build','link','run'))
    depends_on('omega-h@11.0.0-scorec:+kokkos+mpi~trilinos',type=('build','link','run'))

    def cmake_args(self):
        # FIXME: Add arguments other than
        # FIXME: CMAKE_INSTALL_PREFIX and CMAKE_BUILD_TYPE
        # FIXME: If not needed delete this function
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", 'shared')
        ]
        return args
