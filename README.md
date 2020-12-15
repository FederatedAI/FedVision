## FedVision

[![Build Status](https://travis-ci.com/weiwee/FedVision.svg?token=M1cDYtJimwVq7j3Qq2c1&branch=master)](https://travis-ci.com/weiwee/FedVision)
[![codecov](https://codecov.io/gh/weiwee/FedVision/branch/master/graph/badge.svg?token=53P5W56MIJ)](https://codecov.io/gh/weiwee/FedVision)
[![Documentation Status](https://readthedocs.com/projects/sagewei-fedvision/badge/?version=latest&token=b5f872239fae7a1fb71abee19971fa6916d14cc10af496affd92446f64a7f75f)](https://sagewei-fedvision.readthedocs-hosted.com/en/latest/?badge=latest)

FedVison is a Visual Object Detection Platform Powered by Federated Learning


### quick start

#### install

clone repos
``` bash
git clone --recursive https://github.com/weiwee/FedVision.git
cd FedVision
```

create virtualenv and install requirements
```bash
virtualenv .venv --python=3.7
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

build proto
```bash
python tools/protobuf build
```

start service
```bash
sh bin/run.sh
```
run examples
```bash
cd examples/paddle_detection
sh run.sh
```
