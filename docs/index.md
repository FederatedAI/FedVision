## Welcome to FedVision

[![Build Status](https://travis-ci.com/weiwee/FedVision.svg?token=M1cDYtJimwVq7j3Qq2c1&branch=master)](https://travis-ci.com/weiwee/FedVision)
[![codecov](https://codecov.io/gh/weiwee/FedVision/branch/master/graph/badge.svg?token=53P5W56MIJ)](https://codecov.io/gh/weiwee/FedVision)
[![Documentation Status](https://readthedocs.com/projects/sagewei-fedvision/badge/?version=latest&token=b5f872239fae7a1fb71abee19971fa6916d14cc10af496affd92446f64a7f75f)](https://sagewei-fedvision.readthedocs-hosted.com/en/latest/?badge=latest)

FedVison is a Visual Object Detection Platform Powered by Federated Learning


### quick start

#### install

![install](img/install.gif)

clone repos
``` bash
git clone --recursive https://github.com/weiwee/FedVision.git
cd FedVision
```

create virtualenv and install requirements
```bash
virtualenv .venv --python=3.6
source .venv/bin/activate
pip install -r requirements.txt
```

install FedVision in develop mode
```bash
python setup.py develop
```

run scripts
```bash
compile --ppdet -c configs/yolov3_mobilenet_v1_fruit.yml
scheduler
server
triner --ppdet -c configs/yolov3_mobilenet_v1_fruit.yml
```

#### build docs

we use [mkdocs](https://www.mkdocs.org/) with theme [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) for documents generation.

install mkdocs
```bash
pip install mkdocs, mkdocs-material, python-markdown-math
```

start serve
```
mkdocs serve
```

check localhost:8000 in browser
