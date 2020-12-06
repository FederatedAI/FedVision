from setuptools import setup
from setuptools import find_packages
from fedvision import __version__

PADDLE_DETECTION_REQUIRED_PACKAGES = []
REQUIRED_PACKAGES = []

setup(
    name="FedVision",
    version=__version__,
    description="A Visual Object Detection Platform Powered by Federated Learning",
    long_description="",
    license="",
    url="https://github.com/weiwee/FedVision",
    author="FATE authors",
    author_email="FATE-dev@webank.com",
    maintainer="Sage Wei",
    maintainer_email="wbwmat@gmail.com",
    packages=find_packages(".", include=["fedvision*", "deps"]),
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES + PADDLE_DETECTION_REQUIRED_PACKAGES,
    package_data={"": ["*"]},
    entry_points={"console_scripts": []},
)
