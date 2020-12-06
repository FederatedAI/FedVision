### develop

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
