## FedVision Deploy Toolkit

### Build package

```bash
git clone https://github.com/FederatedAI/FedVision
python3 -m venv venv
source venv/bin/activate
pip install -r FedVision/requirements.txt
pip install -r FedVision/requirements_dev.txt
python FedVision/tools/protobuf.py build
cd FedVision/deploy/deploy_tookit
export PYTHONPATH=$(pwd)
python fedvision_deploy_toolkit/_build.py

# build
pip install pep517
python -m pep517.build .
```

### Usage

See `Deploy` section in online documents:

- [![Documentation Read the Docs](https://img.shields.io/readthedocs/fedvision?label=Read%20the%20Docs)](https://fedvision.readthedocs.io/en/latest/?badge=latest)

- [![Documentation Github Page](https://github.com/FederatedAI/FedVision/workflows/GitHub%20Pages/badge.svg)](http://federatedai.github.io/FedVision)
