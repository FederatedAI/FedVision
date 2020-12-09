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
from pathlib import Path

import click
from fedvision import __basedir__


@click.command()
@click.option("--ps-endpoint", type=str)
@click.option("--num-worker", type=int)
@click.option("--config", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option(
    "--algorithm-config", type=click.Path(exists=True, file_okay=True, dir_okay=False)
)
def fl_master(algorithm_config, config, ps_endpoint, num_worker):
    from paddle_fl.paddle_fl.core.master.job_generator import JobGenerator
    from paddle_fl.paddle_fl.core.strategy.fl_strategy_base import FedAvgStrategy

    with open(config) as f:
        config_json = json.load(f)

    strategy = FedAvgStrategy()
    strategy.fed_avg = True
    strategy.inner_step = config_json["inner_step"]

    endpoints = [ps_endpoint]
    job_generator = JobGenerator()
    job_generator.generate_fl_job_from_program(
        strategy=strategy,
        endpoints=endpoints,
        worker_num=num_worker,
        program_input=f"{Path(__basedir__).joinpath('paddle_fl/tasks/cli/faster_rcnn/program')}",
        output="compile",
    )


if __name__ == "__main__":
    fl_master()
