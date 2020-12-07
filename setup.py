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

from setuptools import setup
from setuptools import find_packages
from fedvision import __version__

REQUIRED_PACKAGES = [
    "attr",
    "grpcio>=1.33.2,!=1.34.0",
    "grpcio-tools>=1.33.2,!=1.34.0",
    "aiohttp>=3.7,<3.8",
    "loguru>=0.5",
    "protobuf==3.14.0",
    "jsonschema==3.2.0",
    "PyYAML>=5.3.1",
    "click==7.1.2",
    "paddlepaddle==1.8.5",
]

setup(
    name="FedVision",
    version=__version__,
    description="A Visual Object Detection Platform Powered by Federated Learning",
    long_description="",
    license="",
    url="https://github.com/FederatedAI/FedVision",
    author="FATE authors",
    author_email="FATE-dev@webank.com",
    maintainer="Sage Wei",
    maintainer_email="wbwmat@gmail.com",
    packages=find_packages(".", include=["fedvision*", "deps"]),
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES,
    package_data={"": ["*"]},
    entry_points={"console_scripts": []},
)
