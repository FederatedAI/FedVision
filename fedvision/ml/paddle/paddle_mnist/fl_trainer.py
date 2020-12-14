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
import paddle

from fedvision.paddle_fl.tasks.utils import FedAvgTrainer


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
    "--feeds",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--config",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--algorithm-config",
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
    feeds,
    config,
    algorithm_config,
):
    import numpy as np
    import paddle.fluid as fluid

    from ppdet.utils import checkpoint

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
    device = config_json.get("device", "cpu")
    use_vdl = config_json.get("use_vdl", False)

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
    feed_list = trainer.load_feed_list(feeds)
    feeder = fluid.DataFeeder(feed_list=feed_list, place=place)
    logging.debug(f"data loader ready")

    epoch_id = -1
    step = 0

    mnist_loader = paddle.batch(
        fluid.io.shuffle(paddle.dataset.mnist.train(), 1000), 128
    )

    if use_vdl:
        from visualdl import LogWriter

        vdl_writer = LogWriter("vdl_log")

    while epoch_id < max_iter:
        epoch_id += 1
        if not trainer.scheduler_agent.join(epoch_id):
            logging.debug(f"not join, waiting next round")
            continue

        logging.debug(f"epoch {epoch_id} start train")

        for step_id, data in enumerate(mnist_loader()):
            outs = trainer.run(feeder.feed(data), fetch=trainer._target_names)
            if use_vdl:
                stats = {
                    k: np.array(v).mean() for k, v in zip(trainer._target_names, outs)
                }
                for loss_name, loss_value in stats.items():
                    vdl_writer.add_scalar(loss_name, loss_value, step)
            step += 1
            logging.debug(f"step: {step}, outs: {outs}")

        # save model
        logging.debug(f"saving model at {epoch_id}-th epoch")
        trainer.save_model(f"model/{epoch_id}")

        # info scheduler
        trainer.scheduler_agent.finish()
        checkpoint.save(trainer.exe, trainer._main_program, f"checkpoint/{epoch_id}")

    logging.debug(f"reach max iter, finish training")


if __name__ == "__main__":
    fl_trainer()
