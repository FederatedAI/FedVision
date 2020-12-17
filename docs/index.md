## Welcome to FedVision

[![Build Status](https://travis-ci.com/weiwee/FedVision.svg?token=M1cDYtJimwVq7j3Qq2c1&branch=master)](https://travis-ci.com/weiwee/FedVision)
[![codecov](https://codecov.io/gh/weiwee/FedVision/branch/master/graph/badge.svg?token=53P5W56MIJ)](https://codecov.io/gh/weiwee/FedVision)
[![Documentation Status](https://readthedocs.com/projects/sagewei-fedvision/badge/?version=latest&token=b5f872239fae7a1fb71abee19971fa6916d14cc10af496affd92446f64a7f75f)](https://sagewei-fedvision.readthedocs-hosted.com/en/latest/?badge=latest)

FedVision is a Visual Object Detection Platform Powered by Federated Learning


### quick start

1. install deploy toolkit

    ``` bash
    pip install -U pip && pip install fedvision_deploy_toolkit
    ```

2. generate deploy template

    ```bash
    fedvision-deploy template generate
    ```

3. modify generated template `deploy_config_template.yaml` according to comments.

4. start service
    
   ```bash
   fedvision-deploy deploy deploy deploy_config_template.yaml
   ```
5. run examples in deploy directory

   1) download data with script in ${deploy_dir}/data
   2) run examples with script in ${deploy_dir}/examples

