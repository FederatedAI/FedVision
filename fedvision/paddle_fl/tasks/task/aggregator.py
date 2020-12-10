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

import sys

from fedvision.framework.abc.executor import Executor
from fedvision.framework.abc.task import Task
from fedvision.framework.protobuf import job_pb2
from fedvision.framework.utils.exception import FedvisionWorkerException
from fedvision.paddle_fl.protobuf import fl_job_pb2


class FLAggregator(Task):
    task_type = "fl_aggregator"

    def __init__(
        self,
        job_id,
        task_id,
        scheduler_ep,
        main_program,
        startup_program,
        config_string,
    ):
        super().__init__(job_id=job_id, task_id=task_id)
        self._scheduler_ep = scheduler_ep
        self._main_program = main_program
        self._startup_program = startup_program
        self._config_string = config_string

    @classmethod
    def deserialize(cls, pb: job_pb2.Task) -> "FLAggregator":
        if pb.task_type != cls.task_type:
            raise FedvisionWorkerException(
                f"try to deserialize task_type {pb.task_type} by {cls.task_type}"
            )
        scheduler_task_pb = fl_job_pb2.PaddleFLAggregatorTask()
        pb.task.Unpack(scheduler_task_pb)
        return FLAggregator(
            job_id=pb.job_id,
            task_id=pb.task_id,
            scheduler_ep=scheduler_task_pb.scheduler_ep,
            startup_program=scheduler_task_pb.startup_program,
            main_program=scheduler_task_pb.main_program,
            config_string=scheduler_task_pb.config_string,
        )

    async def exec(self, executor: Executor):
        python_executable = sys.executable
        cmd = " ".join(
            [
                f"{python_executable} -m fedvision.paddle_fl.tasks.cli.fl_scheduler",
                f"--scheduler-ep={self._scheduler_ep}",
                f"--startup-program=startup_program",
                f"--main-program=main_program",
                f"--config=config.json",
                f">{executor.stdout} 2>{executor.stderr}",
            ]
        )
        with executor.working_dir.joinpath("main_program").open("wb") as f:
            f.write(self._main_program)
        with executor.working_dir.joinpath("startup_program").open("wb") as f:
            f.write(self._startup_program)
        with executor.working_dir.joinpath("config.json").open("w") as f:
            f.write(self._config_string)
        returncode = await executor.execute(cmd)
        if returncode != 0:
            raise FedvisionWorkerException(
                f"execute task: {self.task_id} failed, return code: {returncode}"
            )
