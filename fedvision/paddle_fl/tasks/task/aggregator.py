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
        worker_num,
        max_iter,
        main_program,
        startup_program,
    ):
        super().__init__(job_id=job_id, task_id=task_id)
        self._scheduler_ep = scheduler_ep
        self._worker_num = worker_num
        self._max_iter = max_iter
        self._main_program = main_program
        self._startup_program = startup_program

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
            worker_num=scheduler_task_pb.worker_num,
            max_iter=scheduler_task_pb.max_iter,
            startup_program=scheduler_task_pb.startup_program,
            main_program=scheduler_task_pb.main_program,
        )

    async def exec(self, executor: Executor):
        python_executable = sys.executable
        cmd = " ".join(
            [
                f"{python_executable} -m fedvision.paddle_fl.tasks.cli.fl_scheduler",
                f"--scheduler-ep={self._scheduler_ep}",
                f"--worker-num={self._worker_num}",
                f"--max-iter={self._max_iter}",
                f"--startup-program=startup_program",
                f"--main-program=main_program",
                f">{executor.stdout} 2>{executor.stderr}",
            ]
        )
        with executor.working_dir.joinpath("main_program").open("wb") as f:
            f.write(self._main_program)
        with executor.working_dir.joinpath("startup_program").open("wb") as f:
            f.write(self._startup_program)
        returncode = await executor.execute(cmd)
        if returncode != 0:
            raise FedvisionWorkerException(
                f"execute task: {self.task_id} failed, return code: {returncode}"
            )
