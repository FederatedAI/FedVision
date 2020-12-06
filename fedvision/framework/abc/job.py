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

    def compile(self):
        ...

    @abc.abstractmethod
    def generate_proposal_request(self) -> coordinator_pb2.Proposal.REQ:
        ...

    @abc.abstractmethod
    def generate_local_tasks(self) -> List[job_pb2.Task]:
        ...

    @classmethod
    @abc.abstractmethod
    def load(cls, job_id: str, config) -> "Job":
        ...

    def generate_task_id(self, task_name):
        return f"{self.job_id}-task_{task_name}"
