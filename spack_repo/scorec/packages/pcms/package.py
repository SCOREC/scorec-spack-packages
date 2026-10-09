# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

#from spack import *
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack.package import *


class Pcms(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    homepage      = "https://github.com/SCOREC/pcms"
    git      = "https://github.com/SCOREC/pcms"
    maintainers = ['jacobmerson','cwsmith']

    #version('0.0.5', tag='v0.0.5') 
    version('0.0.5', commit='12d609cc2622c62b7d43263812fb8403a0a5f6ef')
    version('develop', branch='develop')

    # cannot build without omega_h
    #variant('omega-h', default=True, description='enable Omega-h for unstructured meshes')
    variant('client', default=True, description='enable pcms client code')
    variant('server', default=True, description='enable pcms client code')
    variant('tests', default=True, description='enable test cases')
    variant('shared', default=True, description='enable shared library builds')
    variant('fortran', default=True, description='enable fortran interfaces')
    variant('python', default=False, description='enable python interfaces')
    variant('netcdf', default=False, description='link against netcdf for vmec read')
    variant('petsc', default=False, description='link against petsc, required for conservative field transfer')
    variant('meshfields', default=True, description='link against mesh fields for FEM field evaluation')
    variant('sundials', default=False, description='link against sundials for adaptive transient timestepping')

    depends_on('redev@main', when='@develop')
    depends_on('redev@4.3.1:',type=('build','link','run'))
    depends_on('kokkos', type=('build','link','run'))
    depends_on('kokkos-kernels', type=('build','link','run'))
    depends_on('omega-h@11.0.0-scorec:+kokkos~trilinos+mpi')
    depends_on('omega-h+python+shared', when="+shared")
    #depends_on('fftw',type=('build','link','run'))
    depends_on('catch2@3:', when='@0.0.6:+tests',type=('build','link','run'))
    depends_on('catch2@2:2.99', when='@:0.0.5+tests',type=('build','link','run'))
    depends_on('perfstubs',type=('build','link','run'))
    depends_on('adios2+fortran@2.10.2',when="+fortran",type=('build', 'link','run'))
    depends_on('meshfields+shared', when="@develop+python")
    depends_on('meshfields+shared', when="+shared")
    depends_on('meshfields', when='@develop')
    depends_on('meshfields', when='+meshfields')
    depends_on('petsc+kokkos', when="@develop+petsc")
    # PETSc only enables CUDA from its own +cuda variant (it does not follow the
    # Kokkos backend), and petsc~cuda fails to configure against a CUDA Kokkos.
    # Key PETSc's CUDA off the Kokkos we build against, as pumi-tally does.
    for arch in CudaPackage.cuda_arch_values:
        cuda_dep = f"+cuda cuda_arch={arch}"
        depends_on(f"petsc {cuda_dep}", when=f"@develop+petsc ^kokkos {cuda_dep}")
    depends_on('sundials', when="+sundials")
    depends_on('c')
    depends_on('cxx')
    depends_on('fortran', when='+fortran')
    depends_on('python', when='+python')
    depends_on('py-pybind11', type='build', when='+python')
    depends_on('py-numpy', type=('build','link','run'), when='+python')
    depends_on('netcdf-c build_system=cmake', when='+netcdf')

    extends('python', when='+python')


    resource(name='testdata',
            git='https://github.com/SCOREC/pcms_testcases.git',
            branch='main',
            placement='testdata')

    def cmake_args(self):
        prefix = "PCMS"
        if self.spec.satisfies("@:0.0.5"):
            prefix = "WDMCPL"
        args = [
                self.define(f"{prefix}_ENABLE_OMEGA_H", True),
                self.define_from_variant(f"{prefix}_ENABLE_SERVER", 'server'),
                self.define_from_variant(f"{prefix}_ENABLE_CLIENT", 'client'),
                self.define_from_variant("BUILD_TESTING", 'tests'),
                self.define_from_variant("BUILD_SHARED_LIBS", 'shared'),
                self.define(f'{prefix}_ENABLE_SPDLOG', False),
                self.define(f'{prefix}_ENABLE_C', True),
                self.define_from_variant(f'{prefix}_ENABLE_Fortran', 'fortran'),
                self.define_from_variant(f'{prefix}_ENABLE_Python', 'python'),
                self.define(f'{prefix}_TEST_DATA_DIR', self.stage.source_path+'/testdata'),
                self.define_from_variant(f'{prefix}_ENABLE_NETCDF', 'netcdf'),
                self.define_from_variant(f'{prefix}_ENABLE_PETSC', 'petsc'),
                self.define_from_variant(f'{prefix}_ENABLE_MESHFIELDS', 'meshfields'),
                self.define_from_variant(f'{prefix}_ENABLE_SUNDIALS', 'sundials')
                ]
        args.append(self.define("perfstubs_DIR",self.spec["perfstubs"].libs.directories[0] + "/cmake" ))
        return args

    # modify the default behavior in lib/spack/build_systems/cmake.py
    # to not use parallel builds
    def check(self):
        """Searches the CMake-generated Makefile for the target ``test``
        and runs it if found.
        """
        with working_dir(self.build_directory):
            if self.generator == 'Unix Makefiles':
                self._if_make_target_execute('test',
                                             jobs_env='CTEST_PARALLEL_LEVEL',parallel=False)
                self._if_make_target_execute('check',parallel=False)
            elif self.generator == 'Ninja':
                self._if_ninja_target_execute('test',
                                              jobs_env='CTEST_PARALLEL_LEVEL',parallel=False)
                self._if_ninja_target_execute('check',parallel=False)
