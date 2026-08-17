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
#     spack install py-dill
#
# You can edit this file again by typing:
#
#     spack edit py-dill
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.python import PythonPackage
from spack.package import *


class PyDill(PythonPackage):
    """dill extends Python’s pickle module for serializing and de-serializing Python objects to the majority of the built-in Python types."""

    homepage = "https://pypi.org/project/dill"
    pypi = "dill/dill-0.3.9.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("BSD-3", checked_by="github_user1")

    version("0.3.9", sha256="81aa267dddf68cbfe8029c42ca9ec6a4ab3b22371d1c450abc54422577b4512c")

    # FIXME: Add a build backend, usually defined in pyproject.toml. If no such file
    # exists, use setuptools.
    depends_on("py-setuptools@42:", type="build")

    # FIXME: Add additional dependencies if required.
    #depends_on("py-ctypes", type=("build", "run"))

    #def config_settings(self, spec, prefix):
    #    # FIXME: Add configuration settings to be passed to the build backend
    #    # FIXME: If not needed, delete this function
    #    settings = {}
    #    return settings
