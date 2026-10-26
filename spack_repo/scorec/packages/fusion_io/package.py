# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack_repo.builtin.packages.fusion_io.package import FusionIo as BuiltinFusionIo

from spack.package import *


class FusionIo(BuiltinFusionIo):
    """Builtin fusion-io plus fixes that are not upstream yet, so that projects
    such as pcms can use its installed CMake package.

    The miracl repository carries the same fixes on its own fusion-io recipe.
    """

    # The build finds HDF5 with pkg-config.
    depends_on("pkgconfig", type="build")

    # The trace programs link LAPACK (plot_dr, trace/CMakeLists.txt), which the
    # recipe does not declare. Drop this once the recipe depends on LAPACK.
    depends_on("blas", when="+trace")
    depends_on("lapack", when="+trace")

    # plot_dr uses libm but does not link it.
    patch("fusionio-plot_dr-libm.patch", when="+trace")
    # The exported targets link PkgConfig::HDF5, which the installed config
    # never creates, so find_package(fusionio) fails in every consumer.
    patch("fusionio-config-hdf5-pkgconfig.patch")

    def cmake_args(self):
        args = super().cmake_args()
        # Only static libraries are installed; consumers such as pcms link them
        # into shared libraries.
        args.append(self.define("CMAKE_POSITION_INDEPENDENT_CODE", True))
        if self.spec.satisfies("+trace"):
            args += [
                self.define("BLAS_LIBRARIES", self.spec["blas"].libs.joined(";")),
                self.define("LAPACK_LIBRARIES", self.spec["lapack"].libs.joined(";")),
            ]
        return args
