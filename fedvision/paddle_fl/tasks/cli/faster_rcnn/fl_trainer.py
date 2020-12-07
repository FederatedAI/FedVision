# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright (c) 2020 The FedVision Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

import click
import paddle.fluid as fluid

from fedvision.paddle_fl.data.loader import DataReader
from fedvision.paddle_fl.tasks._trainer import FedAvgTrainer


@click.command()
@click.option("--scheduler-ep", type=str, required=True)
@click.option("--trainer-id", type=int, required=True)
@click.option("--trainer-ep", type=str, required=True)
@click.option(
    "--main-program",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--startup-program",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--send-program",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--recv-program",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--feed-names",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--target-names",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--strategy",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--config",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
def fl_trainer(
    trainer_id: int,
    trainer_ep: str,
    scheduler_ep: str,
    main_program,
    startup_program,
    send_program,
    recv_program,
    feed_names,
    target_names,
    strategy,
    config,
):

    logging.basicConfig(
        filename="trainer.log",
        filemode="w",
        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        datefmt="%d-%M-%Y %H:%M:%S",
        level=logging.DEBUG,
    )
    with open(config) as f:
        config_json = json.load(f)
    max_iter = config_json["max_iter"]
    dataset_dir = config_json["dataset"]
    device = config_json.get("device", "cpu")
    logging.debug(f"training program begin")
    trainer = FedAvgTrainer(scheduler_ep=scheduler_ep, trainer_ep=trainer_ep)
    logging.debug(f"job program loading")
    trainer.load_job(
        main_program=main_program,
        startup_program=startup_program,
        send_program=send_program,
        recv_program=recv_program,
        feed_names=feed_names,
        target_names=target_names,
        strategy=strategy,
    )
    logging.debug(f"job program loaded")
    place = fluid.CPUPlace() if device != "cuda" else fluid.CUDAPlace(0)

    logging.debug(f"trainer starting with place {place}")
    trainer.start(place)
    logging.debug(f"trainer stared")

    logging.debug(f"loading data")
    image = fluid.layers.data(
        name="image", shape=[3, None, None], dtype="float32", lod_level=0
    )
    im_info = fluid.layers.data(
        name="im_info", shape=[None, 3], dtype="float32", lod_level=0
    )
    im_id = fluid.layers.data(name="im_id", shape=[None, 1], dtype="int64", lod_level=0)
    gt_bbox = fluid.layers.data(
        name="gt_bbox", shape=[None, 4], dtype="float32", lod_level=1
    )
    gt_class = fluid.layers.data(
        name="gt_class", shape=[None, 1], dtype="int32", lod_level=1
    )
    is_crowd = fluid.layers.data(
        name="is_crowd", shape=[None, 1], dtype="int32", lod_level=1
    )
    feeder = fluid.DataFeeder(
        feed_list=[image, im_info, im_id, gt_bbox, gt_class, is_crowd], place=place
    )
    logging.debug(f"data loader ready")

    epoch_id = -1
    step = 0

    while epoch_id < max_iter:
        epoch_id += 1
        if not trainer.scheduler_agent.join(epoch_id):
            logging.debug(f"not join, waiting next round")
            continue

        logging.debug(f"epoch {epoch_id} start train")
        dataset = DataReader(trainer_id, dataset=dataset_dir)
        data_loader = dataset.data_loader()
        for step_id, data in enumerate(data_loader):
            acc = trainer.run(feeder.feed(data), fetch=["sum_0.tmp_0"])
            step += 1
            logging.debug(f"step: {step}, loss: {acc}")

        # save model
        trainer.save_model(f"model/{epoch_id}")

        # info scheduler
        trainer.scheduler_agent.finish()


if __name__ == "__main__":
    fl_trainer()
