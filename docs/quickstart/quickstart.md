This section describes how to quick deploy and run examples in standalone version of `FedVision`

### Prerequisites

Too run Fedvision, following dependency or tools required:

- machine to install fedvision-deploy-toolkit:

    - python virtualenv with Python>=3
    
    - setup SSH password less login to machine(s) for deploy fedvision framework.

- machine(s) to deploy fedvision framework:
    
    - Python>=3.7(with pip)
    
    - an isolated directory (each directory will be deployed with a copy of code)

### Deploy


<div class="termy">

```console
// create and activate python virtual environment
$ python3 -V
Python 3.9.0
$ python3 -m venv venv && source venv/bin/activate

// install fedvision_deploy_toolkit 
$ (venv) python -m pip install -U pip && python -m pip install fedvision_deploy_toolkit
---> 100%
Successfully installed fedvision_deploy_toolkit 

// generate deploy template
$ (venv) fedvision-deploy template standalone

// read comments in generated template standalone_template.yaml` and modify as you want.


// deploy now
$ (venv) fedvision-deploy deploy deploy standalone_template.yaml
deploying 2 machines: ['machine1']
---> 100%
deploy done

```

</div>

!!! note
    Deploying Cluster version is almost same except that you should generate template using
    ```bash
    fedvision-deploy template template
    ```
    and modify generated template file according to comments.

### Services start 

Services could be start/stop with scripts in `Fedvision/sbin` or, use fedvision deploy toolkits:

<div class="termy">

```console
// start services
$ fedvision-deploy services all start standalone_template.yaml

staring coordinator coordinator1
coordinator service start successfully. pid: 92869
127.0.0.1:22:/data/projects/fedvision started coordinator: port=10000
start coordinator coordinator1 done

starting cluster cluster1
clustermanager service start successfully. pid: 92907
127.0.0.1:22:/data/projects/fedvision started cluster manager: port=10001
start cluster cluster1 done, success: True

starting cluster workers for cluster cluster1
starting worker worker1
cluster worker service start successfully. pid: 92944
127.0.0.1:22:/data/projects/fedvision started cluster worker: name=worker1
start worker worker1 done, success: True

starting master master1
master service start successfully. pid: 92975
127.0.0.1:22:/data/projects/fedvision started master: port=10002
start master master1 done, success: True

starting master master2
master service start successfully. pid: 93022
127.0.0.1:22:/data/projects/fedvision started master: port=10003
start master master2 done, success: True

starting master master3
master service start successfully. pid: 93067
127.0.0.1:22:/data/projects/fedvision started master: port=10004
start master master3 done, success: True

starting master master4
master service start successfully. pid: 93112
127.0.0.1:22:/data/projects/fedvision started master: port=10005
start master master4 done, success: True

```

</div>

### Run examples

Jobs could be submitted at each deployed machine with master service started. 


<div class="termy">

```console
$ cd /data/projects/fedvision
$ source venv/bin/activate
$ export PYTHONPATH=$PYTHONPATH:/data/projects/fedvision/FedVision

// submit jobs to master1
$ sh FedVision/examples/paddle_mnist/run.sh 127.0.0.1:10002
{
  "job_id": "master1-20201218202835-1"
} 
```

</div>

**Note**: find logs in /data/projects/fedvision/FedVision/logs