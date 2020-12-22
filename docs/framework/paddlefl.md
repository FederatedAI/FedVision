We provide a mnist demo to describes how to implement a job directly from `PaddleFL`.

There are two `py` file related:

1. [fl_master](https://github.com/FederatedAI/FedVision/blob/main/fedvision/ml/paddle/paddle_mnist/fl_master.py): define 
CNN network to learning mnist dataset and compiled with `PaddleFL`

2. [fl_trainer](https://github.com/FederatedAI/FedVision/blob/main/fedvision/ml/paddle/paddle_mnist/fl_trainer.py): read dataset and training
with compiled program.

Just implement your demo by mimic this demo as you wish.