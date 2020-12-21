# Copyright (c) 2020 The FedVision Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""We not distribute FedVision directly by pypi
since we have a more proper toolkit: fedvision_deploy_toolkit to deploy|start|stop services distributed.
This setup script will error a hint to tell users to install fedvision_deploy_toolkit
instead of install FedVision directly.
"""

import sys

import setuptools

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Environment :: GPU :: NVIDIA CUDA",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Scientific/Engineering :: Image Recognition",
    "Topic :: Security",
]


def get_version():
    from fedvision import __version__

    return __version__


HINT = "Please install the fedvision_deploy_toolkit package with: pip install fedvision_deploy_toolkit"


if "sdist" not in sys.argv:
    """build source distribution only"""
    raise RuntimeError(HINT)


setuptools.setup(
    name="fedvision",
    version=get_version(),
    description=HINT,
    author="The FedVision Authors",
    author_email="contact@FedAI.org",
    url="https://FedAI.org",
    license="Apache License 2.0",
    classifiers=CLASSIFIERS,
)
