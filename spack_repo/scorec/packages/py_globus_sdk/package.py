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
#     spack install py-globus-sdk
#
# You can edit this file again by typing:
#
#     spack edit py-globus-sdk
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyGlobusSdk(PythonPackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://www.example.com"
    pypi = "globus_sdk/globus_sdk-3.51.0.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("UNKNOWN", checked_by="github_user1")

    version("3.51.0", sha256="e7b59cd4a4c64cb23d92009b0488ad7e975f8a9701b786b49b7043c6240a59a5")

    # depends_on("python@3.8:", type=("build", "run"))

    depends_on("py-setuptools@61.2:", type="build")

    # FIXME: Add additional dependencies if required.
    depends_on("py-requests@2.19.1:3.0.0", type=("build", "run"))
    depends_on("py-pyjwt+crypto@2.0.0:3.0.0", type=("build", "run"))
