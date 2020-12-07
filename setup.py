from setuptools import setup
from setuptools import find_packages
from fedvision import __version__

REQUIRED_PACKAGES = [
    "attr",
    "grpcio>=1.33.2,!=1.34.0",
    "grpcio-tools>=1.33.2,!=1.34.0",
    "aiohttp>=3.7,<3.8"
    "loguru>=0.5"
    "protobuf==3.14.0"
    "jsonschema==3.2.0"
    "PyYAML>=5.3.1"
    "click==7.1.2"
    "paddlepaddle==1.8.5",
    "paddle_fl==1.1.0",
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
