# FedVision

[![Documentation Read the Docs](https://img.shields.io/readthedocs/fedvision?label=Read%20the%20Docs)](https://fedvision.readthedocs.io/en/latest/?badge=latest)
[![Documentation Github Page](https://github.com/FederatedAI/FedVision/workflows/GitHub%20Pages/badge.svg)](http://federatedai.github.io/FedVision)
[![Support Python Versions](https://img.shields.io/pypi/pyversions/fedvision)](https://img.shields.io/pypi/pyversions/fedvision)
[![PyPI Version](https://img.shields.io/pypi/v/FedVision)](https://pypi.org/project/fedvision/)


FedVision is a Visual Object Detection Platform Powered by Federated Learning


## Quick start

### Prerequisites

Too run FedVision, following dependency or tools required:

- machine to install fedvision-deploy-toolkit:

    - python virtualenv with Python>=3
    
    - setup SSH password less login to machine(s) for deploy fedvision framework.

- machine(s) to deploy fedvision framework:
    
    - Python>=3.7(with pip)
    
    - an isolated directory (each directory will be deployed with a copy of code)

### Deploy

1. install fedvision deploy toolkit

    ``` bash
    # ceate a python virtual envirement (recommanded) or use an exist one.
    source <virtualenv>/bin/activate
    python -m pip install -U pip && python -m pip install fedvision_deploy_toolkit
    ```

2. generate deploy template

    ```bash
    fedvision-deploy template standalone
    ```

3. read comments in generated template `standalone_template.yaml` and modify as you want.

4. run deploy cmd
    
    ```bash
    fedvision-deploy deploy deploy standalone_template.yaml
    ```

### Services start and stop 

Services could be start/stop with scripts in `Fedvision/sbin` or, use fedvision deploy toolkits:

```bash
fedvision-deploy services all start standalone_template.yaml
```

### Run examples

Jobs could be submitted at each deployed machine with master service started. 

```bash
cd /data/projects/fedvision
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/data/projects/fedvision/FedVision
sh FedVision/examples/paddle_mnist/run.sh 127.0.0.1:10002
```

## Framework


![framework](docs/img/fedvision.png)


## Documentation

Documentation can be generated using [Mkdocs](https://www.mkdocs.org/). 
Users can build the documentation using

```
source venv/bin/activate # venv to build docs
pip install -r requirement.txt
pip install -r docs/requirements.txt
mkdocs serve
```

Open up http://127.0.0.1:8000/ in your browser.

The latest version of online documentation can be found at

- [![Documentation Read the Docs](https://img.shields.io/readthedocs/fedvision?label=Read%20the%20Docs)](https://fedvision.readthedocs.io/en/latest/?badge=latest)

- [![Documentation Github Page](https://github.com/FederatedAI/FedVision/workflows/GitHub%20Pages/badge.svg)](http://federatedai.github.io/FedVision)

## License

FedVision is released under Apache License 2.0. 
Please note that third-party libraries may not have the same license as FedVision.

## Contributing

Any contributions you make are greatly appreciated!

- Please report bugs by submitting a GitHub issue.

- Please submit contributions using pull requests.