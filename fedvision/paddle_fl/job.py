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
import sys
from pathlib import Path
from typing import List

from fedvision import __logs_dir__
from fedvision.framework.abc.job import Job
from fedvision.framework.cluster.executor import ProcessExecutor
from fedvision.framework.protobuf import job_pb2, coordinator_pb2, cluster_pb2
from fedvision.framework.utils.exception import FedvisionJobCompileException
from fedvision.paddle_fl.protobuf import fl_job_pb2

JOB_TYPE = "paddle_fl"


class PaddleFLJob(Job):
    job_type = JOB_TYPE

    @classmethod
    def load(cls, job_id, config, algorithm_config) -> "PaddleFLJob":
        return PaddleFLJob(
            job_id=job_id,
            proposal_wait_time=config["proposal_wait_time"],
            worker_num=config["worker_num"],
            program=config["program"],
            config=config,
            algorithm_config=algorithm_config,
        )

    def __init__(
        self,
        job_id,
        program,
        proposal_wait_time,
        worker_num,
        config,
        algorithm_config,
    ):
        super().__init__(job_id=job_id)
        self._proposal_wait_time = proposal_wait_time
        self._worker_num = worker_num
        self._program = program
        self._trainer_entrypoint = f"fedvision.ml.paddle.{self._program}.fl_trainer"

        self._config_string = json.dumps(config)
        self._algorithm_config = algorithm_config

    @property
    def resource_required(self):
        return cluster_pb2.TaskResourceRequire.REQ(num_endpoints=2)

    # noinspection PyAttributeOutsideInit
    def set_required_resource(self, response):
        self._server_endpoint = response.endpoints[0]
        self._aggregator_endpoint = response.endpoints[1]
        self._aggregator_assignee = response.worker_id

    @property
    def compile_path(self):
        return Path(__logs_dir__).joinpath(f"jobs/{self.job_id}/master")

    async def compile(self):
        executor = ProcessExecutor(self.compile_path)
        with self.compile_path.joinpath("algorithm_config.yaml").open("w") as f:
            f.write(self._algorithm_config)
        with self.compile_path.joinpath("config.json").open("w") as f:
            f.write(self._config_string)
        executable = sys.executable
        cmd = " ".join(
            [
                f"{executable} -m fedvision.ml.paddle.{self._program}.fl_master",
                f"--ps-endpoint {self._server_endpoint}",
                f"--algorithm-config algorithm_config.yaml",
                f"--config config.json",
                f">{executor.stdout} 2>{executor.stderr}",
            ]
        )
        returncode = await executor.execute(cmd)
        if returncode != 0:

            raise FedvisionJobCompileException("compile error")

    def generate_proposal_request(self) -> coordinator_pb2.Proposal.REQ:
        request = coordinator_pb2.Proposal.REQ(
            job_id=self.job_id,
            job_type=self.job_type,
            proposal_wait_time=self._proposal_wait_time,
            minimum_acceptance=self._worker_num,
            maximum_acceptance=self._worker_num,
        )
        for i in range(self._worker_num):
            task = request.tasks.add()
            self._generate_trainer_task_pb(task, i)
        return request

    def generate_local_tasks(self) -> List[job_pb2.Task]:
        return [
            self._generate_aggregator_task_pb(),
        ]

    def _generate_trainer_task_pb(self, task_pb, i):
        trainer_pb = fl_job_pb2.PaddleFLWorkerTask(
            scheduler_ep=self._aggregator_endpoint,
            trainer_id=i,
            trainer_ep=f"trainer_{i}",
            entrypoint=self._trainer_entrypoint,
            main_program=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{i}/trainer.main.program")
            ),
            startup_program=_load_program_bytes(
                self.compile_path.joinpath(
                    f"compile/trainer{i}/trainer.startup.program"
                )
            ),
            send_program=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{i}/trainer.send.program")
            ),
            recv_program=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{i}/trainer.recv.program")
            ),
            feed_names=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{i}/feed_names")
            ),
            target_names=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{i}/target_names")
            ),
            strategy=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{i}/strategy.pkl")
            ),
            feeds=_load_program_bytes(
                self.compile_path.joinpath(f"compile/trainer{1}/feeds.pkl")
            ),
            config_string=self._config_string,
            algorithm_config_string=self._algorithm_config,
        )
        task_pb.job_id = self.job_id
        task_pb.task_id = f"trainer_{i}"
        task_pb.task_type = "fl_trainer"
        task_pb.task.Pack(trainer_pb)
        return task_pb

    def _generate_aggregator_task_pb(self):
        scheduler_pb = fl_job_pb2.PaddleFLAggregatorTask(
            scheduler_ep=self._aggregator_endpoint,
        )
        scheduler_pb.main_program = _load_program_bytes(
            self.compile_path.joinpath(f"compile/server0/server.main.program")
        )
        scheduler_pb.startup_program = _load_program_bytes(
            self.compile_path.joinpath(f"compile/server0/server.startup.program")
        )
        scheduler_pb.config_string = self._config_string

        task_pb = job_pb2.Task(
            job_id=self.job_id,
            task_id=f"aggregator",
            task_type="fl_aggregator",
            assignee=self._aggregator_assignee,
        )
        task_pb.task.Pack(scheduler_pb)
        return task_pb


def _load_program_bytes(path: Path):
    with path.open("rb") as f:
        return f.read()
