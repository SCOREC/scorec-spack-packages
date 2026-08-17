# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

#from spack import *
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

class Redev(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://scorec.github.io/redev/"
    git      = "https://github.com/SCOREC/redev"

    maintainers = ['jacobmerson','cwsmith']

    # FIXME: Add proper versions and checksums here.
    # version('1.2.3', '0123456789abcdef0123456789abcdef')
    version('4.3.1', tag='v4.3.1')
    version('main', branch='main')

    variant('shared', default=True, description='enable shared library builds')

    depends_on('mpi')
    depends_on('adios2@2.7.1:')
    depends_on('perfstubs')
    depends_on('c')
    depends_on('cxx')

    def cmake_args(self):
        args = []
        if 'sst' in self.spec["adios2"]:
            args.append(self.define("ADIOS2_HAVE_SST", True))
        args.append(self.define("perfstubs_DIR",self.spec["perfstubs"].libs.directories[0]+"/cmake"))
        args.append(self.define_from_variant("BUILD_SHARED_LIBS", 'shared'))
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
