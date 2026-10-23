# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

#from spack import *
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack.package import *


class Pcms(CMakePackage, CudaPackage):
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
    variant('gnet', default=False, description='build the GNET to GTC mapping library and gnet2gtc tool')

    depends_on('redev@main', when='@develop')
    depends_on('redev@4.3.1:',type=('build','link','run'))
    depends_on('kokkos', type=('build','link','run'))
    depends_on('kokkos-kernels', type=('build','link','run'))
    depends_on('omega-h@11.0.0-scorec:+kokkos~trilinos+mpi')
    depends_on('omega-h+shared', when="+shared")
    # 11.4.0-scorec is first version with pybind11 as private dependency
    depends_on('omega-h@11.4.0-scorec:+python', when="+python")
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
    depends_on('sundials', when="+sundials")
    depends_on('hdf5', when="+gnet")
    depends_on('c')
    depends_on('cxx')
    depends_on('fortran', when='+fortran')
    depends_on('python', when='+python')
    depends_on('py-pybind11', type='build', when='+python')
    depends_on('py-numpy', type=('build','link','run'), when='+python')
    depends_on('py-pytest', type='test', when='+tests+python')
    depends_on('netcdf-c build_system=cmake', when='+netcdf')
    # pcms_testcases stores large files with git-lfs
    depends_on('git-lfs', type='build', when='+tests')

    extends('python', when='+python')

    # Propagate cuda_arch to dependencies, see https://github.com/spack/spack/issues/28714
    for arch in CudaPackage.cuda_arch_values:
        cuda_dep = '+cuda cuda_arch={0}'.format(arch)
        depends_on('kokkos {0}'.format(cuda_dep), when=cuda_dep)
        depends_on('kokkos-kernels {0}'.format(cuda_dep), when=cuda_dep)
        depends_on('meshfields {0}'.format(cuda_dep), when='{0} ^meshfields'.format(cuda_dep))
        depends_on('petsc {0}'.format(cuda_dep), when='@develop+petsc {0}'.format(cuda_dep))

    conflicts('cuda_arch=none', when='+cuda', msg='CUDA architecture is required')
    conflicts('+gnet', when='@:0.0.5', msg='GNET support was added after 0.0.5')
    # Builds through kokkos's nvcc_wrapper, so +cuda must match Kokkos's backend
    conflicts('~cuda', when='^kokkos+cuda', msg='PCMS requires +cuda when Kokkos has +cuda')
    conflicts('+cuda', when='^kokkos~cuda', msg='PCMS requires Kokkos+cuda when CUDA is enabled')


    resource(name='testdata',
            git='https://github.com/SCOREC/pcms_testcases.git',
            branch='main',
            placement='testdata', when="+tests")

    # Spack's git fetcher has no LFS support, so the resource only contains
    # LFS pointer files. Pull the real content once git-lfs is available.
    @run_before('cmake')
    def fetch_lfs_testdata(self):
        if not self.spec.satisfies('+tests'):
            return
        with working_dir(join_path(self.stage.source_path, 'testdata')):
            git = which('git', required=True)
            git('lfs', 'pull')

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
                self.define_from_variant(f'{prefix}_ENABLE_SUNDIALS', 'sundials'),
                self.define_from_variant(f'{prefix}_ENABLE_GNET', 'gnet')
                ]
        args.append(self.define("perfstubs_DIR",self.spec["perfstubs"].libs.directories[0] + "/cmake" ))
        if self.spec.satisfies("+python"):
            args.append(self.define("PCMS_PYTHON_INSTALL_LOCATION", python_platlib))
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

    @run_after('install')
    def cache_test_sources(self):
        srcs = ['examples/external-usage-example']
        if self.spec.satisfies('+python'):
            srcs += ['test/python', 'examples/python-api-example']
        cache_extra_test_sources(self, srcs)

    def test_python_import(self):
        """Check that the installed Python module can be imported"""
        if not self.spec.satisfies("+python"):
            raise SkipTest("Package must be built with +python")
        python = self.spec["python"].command
        python("-c", "import pcms")

    def test_external_usage(self):
        """build and run a project that uses the installed pcms via find_package"""
        src = join_path(self.test_suite.current_test_cache_dir,
                        'examples', 'external-usage-example')
        cmake = which(self.spec['cmake'].prefix.bin.cmake, required=True)
        with working_dir(join_path(src, 'build'), create=True):
            cmake(src,
                  self.define('pcms_ROOT', self.prefix),
                  self.define('CMAKE_C_COMPILER', self['c'].cc),
                  self.define('CMAKE_CXX_COMPILER', self['cxx'].cxx),
                  self.define('MPI_HOME', self.spec['mpi'].prefix))
            cmake('--build', '.')
            pcms_test = which(join_path('.', 'pcms_test'), required=True)
            pcms_test()

    def test_python(self):
        """run the python test suite against the installed module"""
        if not self.spec.satisfies('+python'):
            raise SkipTest('Package must be built with +python')
        python = self.spec['python'].command
        python('-c', 'import pytest', fail_on_error=False, output=str, error=str)
        if python.returncode != 0:
            raise SkipTest('pytest not available; install pcms with --test')
        with working_dir(self.test_suite.current_test_cache_dir):
            python('-m', 'pytest', join_path('test', 'python'), '-p', 'no:cacheprovider')
