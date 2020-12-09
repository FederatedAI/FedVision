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


class FLTrainer(Task):
    task_type = "fl_trainer"

    def __init__(
        self,
        job_id,
        task_id,
        scheduler_ep: str,
        trainer_id: int,
        trainer_ep: str,
        entrypoint,
        startup_program,
        main_program,
        send_program,
        recv_program,
        feed_names,
        target_names,
        strategy,
        config_string,
        algorithm_config_string,
    ):
        super().__init__(job_id=job_id, task_id=task_id)
        self._scheduler_ep = scheduler_ep
        self._trainer_id = trainer_id
        self._trainer_ep = trainer_ep
        self._entrypoint = entrypoint
        self._startup_program = startup_program
        self._main_program = main_program
        self._send_program = send_program
        self._recv_program = recv_program
        self._feed_names = feed_names
        self._target_names = target_names
        self._strategy = strategy
        self._config_string = config_string
        self._algorithm_config_string = algorithm_config_string

    @classmethod
    def deserialize(cls, pb: job_pb2.Task) -> "FLTrainer":
        if pb.task_type != cls.task_type:
            raise FedvisionWorkerException(
                f"try to deserialize task_type {pb.task_type} by {cls.task_type}"
            )
        worker_task_pb = fl_job_pb2.PaddleFLWorkerTask()
        pb.task.Unpack(worker_task_pb)
        return FLTrainer(
            job_id=pb.job_id,
            task_id=pb.task_id,
            scheduler_ep=worker_task_pb.scheduler_ep,
            trainer_id=worker_task_pb.trainer_id,
            trainer_ep=worker_task_pb.trainer_ep,
            entrypoint=worker_task_pb.entrypoint,
            startup_program=worker_task_pb.startup_program,
            main_program=worker_task_pb.main_program,
            send_program=worker_task_pb.send_program,
            recv_program=worker_task_pb.recv_program,
            feed_names=worker_task_pb.feed_names,
            target_names=worker_task_pb.target_names,
            strategy=worker_task_pb.strategy,
            config_string=worker_task_pb.config_string,
            algorithm_config_string=worker_task_pb.algorithm_config_string,
        )

    async def exec(self, executor: Executor):
        python_executable = sys.executable
        cmd = " ".join(
            [
                f"{python_executable} -m {self._entrypoint}",
                f"--scheduler-ep={self._scheduler_ep}",
                f"--trainer-id={self._trainer_id}",
                f"--trainer-ep={self._trainer_ep}",
                f"--startup-program=startup_program",
                f"--main-program=main_program",
                f"--send-program=send_program",
                f"--recv-program=recv_program",
                f"--feed-names=feed_names",
                f"--target-names=target_names",
                f"--strategy=strategy",
                f"--config config.json",
                f"--algorithm-config algorithm_config.yaml"
                f">{executor.stdout} 2>{executor.stderr}",
            ]
        )
        with executor.working_dir.joinpath("main_program").open("wb") as f:
            f.write(self._main_program)
        with executor.working_dir.joinpath("startup_program").open("wb") as f:
            f.write(self._startup_program)
        with executor.working_dir.joinpath("send_program").open("wb") as f:
            f.write(self._send_program)
        with executor.working_dir.joinpath("recv_program").open("wb") as f:
            f.write(self._recv_program)
        with executor.working_dir.joinpath("feed_names").open("wb") as f:
            f.write(self._feed_names)
        with executor.working_dir.joinpath("target_names").open("wb") as f:
            f.write(self._target_names)
        with executor.working_dir.joinpath("strategy").open("wb") as f:
            f.write(self._strategy)
        with executor.working_dir.joinpath("config.json").open("w") as f:
            f.write(self._config_string)
        with executor.working_dir.joinpath("algorithm_config.yaml").open("w") as f:
            f.write(self._algorithm_config_string)
        returncode = await executor.execute(cmd)
        if returncode is None or returncode != 0:
            raise FedvisionWorkerException(
                f"execute task: {self.task_id} failed, return code: {returncode}"
            )
