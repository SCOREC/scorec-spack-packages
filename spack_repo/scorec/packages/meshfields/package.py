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
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack.package import *


class Meshfields(CMakePackage, CudaPackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/SCOREC/meshFields"
    git = "https://github.com/SCOREC/meshFields"

    maintainers("jacobmerson")

    license("BSD-3", checked_by="jacobmerson")

    version('main', branch='main')

    variant('shared', default=False, description='enable shared library builds')
    variant('tests', default=False, description='enable build of tests')

    depends_on('cxx')
    depends_on('c') # requires c compiler when building with cabana
    depends_on('cabana@0.7.0:', type=('build', 'link', 'run'))
    # cabana@:0.7 uses Kokkos::MemoryManaged, which kokkos@4.7: only provides
    # with +deprecated_code (removed entirely in 5). Matches the known-working
    depends_on('kokkos@4:4.6', type=('build','link','run'))
    depends_on('kokkos-kernels@4:4.6', type=('build', 'link', 'run'))
    depends_on('omega-h@11.0.0-scorec:+kokkos+mpi~trilinos',type=('build','link','run'))
    depends_on('kokkos+cuda', when='+cuda')
    depends_on('cabana+cuda', when='+cuda')

    # Propagate cuda_arch to dependencies, see https://github.com/spack/spack/issues/28714
    for arch in CudaPackage.cuda_arch_values:
        cuda_dep = '+cuda cuda_arch={0}'.format(arch)
        depends_on('kokkos {0}'.format(cuda_dep), when=cuda_dep)
        depends_on('cabana {0}'.format(cuda_dep), when=cuda_dep)

    conflicts('cuda_arch=none', when='+cuda', msg='CUDA architecture is required')

    def cmake_args(self):
        # FIXME: Add arguments other than
        # FIXME: CMAKE_INSTALL_PREFIX and CMAKE_BUILD_TYPE
        # FIXME: If not needed delete this function
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", 'shared'),
            self.define_from_variant("MeshFields_IS_TESTING", 'tests'),
            self.define("MeshFields_USE_Cabana", True),
        ]
        return args
