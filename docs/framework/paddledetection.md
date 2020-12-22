Federated Job using `PaddleDetection` and `PaddleFL` are supported out of box. To submit a PaddleDetection jobs,
one need a `yaml` config file to describe what algorithm and parameters to used. 
This is almost same as these
[paddle detection configs](https://github.com/PaddlePaddle/PaddleDetection/tree/release/2.0-beta/configs) 
except that reference other config file are not supported. 

One can find an example using yolo mobilenet to detect `fruit` data in [examples](https://github.com/FederatedAI/FedVision/tree/main/examples/paddle_detection).
