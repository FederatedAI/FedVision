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

import abc
from typing import List

from fedvision.framework.protobuf import job_pb2, coordinator_pb2


class Job(metaclass=abc.ABCMeta):

    job_type: str

    def __init__(self, job_id: str):
        self.job_id = job_id

    @property
    def resource_required(self):
        return None

    def set_required_resource(self, response):
        ...

    async def compile(self):
        ...

    @abc.abstractmethod
    def generate_proposal_request(self) -> coordinator_pb2.Proposal.REQ:
        ...

    @abc.abstractmethod
    def generate_local_tasks(self) -> List[job_pb2.Task]:
        ...

    @classmethod
    @abc.abstractmethod
    def load(cls, job_id: str, config, algorithm_config) -> "Job":
        ...

    def generate_task_id(self, task_name):
        return f"{self.job_id}-task_{task_name}"
