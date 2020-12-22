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

from __future__ import annotations

import asyncio
import enum
import json
import traceback
from datetime import datetime
from typing import Optional, MutableMapping, List

import attr
import grpc
from aiohttp import web

from fedvision.framework import extensions
from fedvision.framework.abc.job import Job
from fedvision.framework.protobuf import (
    coordinator_pb2_grpc,
    coordinator_pb2,
    job_pb2,
    cluster_pb2,
    cluster_pb2_grpc,
)
from fedvision.framework.utils.exception import FedvisionExtensionException
from fedvision.framework.utils.logger import Logger


class _JobStatus(enum.Enum):
    """
    query job status
    """

    NOTFOUND = "not_found"
    WAITING = "waiting"
    PROPOSAL = "proposal"
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"


@attr.s
class _SharedStatus(object):
    """
    status shared by ...
    """

    party_id = attr.ib(type=str)
    job_types = attr.ib(type=List[str], default=["paddle_fl", "dummy"])

    def __attrs_post_init__(self):
        self.job_status: MutableMapping[str, _JobStatus] = {}
        self.cluster_task_queue: asyncio.Queue[job_pb2.Task] = asyncio.Queue()
        self.job_queue: asyncio.Queue[Job] = asyncio.Queue()
        self.job_counter = 0

    def generate_job_id(self):
        """
        generate unique job id
        """
        self.job_counter += 1
        return f"{self.party_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.job_counter}"


@attr.s
class ProposalAcceptRule(Logger):
    shared_status = attr.ib(type=_SharedStatus)

    async def accept(self, job_type):
        # accept all
        return job_type in self.shared_status.job_types


class CoordinatorConnect(Logger):
    """
    client connects to coordinator
    """

    def __init__(self, address: str, shared_status: _SharedStatus):
        """
        init coordinator client
        Args:
            address: str
            shared_status:
        """
        self.address = address
        self.shared_status = shared_status
        self.accept_rule = ProposalAcceptRule(self.shared_status)

        self._channel = None
        self._stub = None

    async def subscribe(self):
        """
        start subscribe to coordinator and accept `proposals`
        """
        request = coordinator_pb2.Subscribe.REQ(party_id=self.shared_status.party_id)
        for job_type in self.shared_status.job_types:
            request.job_types.append(job_type)
        async for response in self._stub.Subscribe(request):
            if response.status != coordinator_pb2.Subscribe.SUCCESS:
                return
            if not await self.accept_rule.accept(response.job_type):
                return

            async def _acceptor():
                # accept all
                fetch_response = await self._stub.FetchTask(
                    coordinator_pb2.FetchTask.REQ(
                        party_id=self.shared_status.party_id,
                        proposal_id=response.proposal_id,
                    )
                )
                if fetch_response.status != coordinator_pb2.FetchTask.READY:
                    self.debug(
                        f"proposal {response.proposal_id} not ready: {fetch_response.status}"
                    )
                    return

                # put task in cluster task queue
                await self.shared_status.cluster_task_queue.put(fetch_response.task)

            asyncio.create_task(_acceptor())

    async def make_proposal(
        self, request: coordinator_pb2.Proposal.REQ
    ) -> coordinator_pb2.Proposal.REP:
        """
        publish a job proposal to coordinator
        Args:
            request:
                request

        Returns:
             response

        """
        return await self._stub.Proposal(request)

    async def leave(self):
        """
        disconnect with coordinator
        """
        return await self._stub.Leave(
            coordinator_pb2.Leave.REQ(party_id=self.shared_status.party_id)
        )

    async def start_coordinator_channel(self):
        """
        start channel to coordinator
        """
        self.info(f"start coordinator channel to {self.address}")
        self._channel = grpc.aio.insecure_channel(
            self.address,
            options=[
                ("grpc.max_send_message_length", 512 * 1024 * 1024),
                ("grpc.max_receive_message_length", 512 * 1024 * 1024),
            ],
        )
        self._stub = coordinator_pb2_grpc.CoordinatorStub(
            self._channel,
        )
        self.info(f"coordinator channel started to {self.address}")

    async def coordinator_channel_ready(self):
        """
        wait until channel ready
        """
        return await self._channel.channel_ready()

    async def stop_coordinator_channel(self, grace: Optional[float] = None):
        """
        stop channel
        Args:
            grace:
                wait seconds to gracefully stop
        """
        self.info(f"stopping coordinator channel")
        await self._channel.close(grace)
        self.info(f"coordinator channel started to {self.address}")


class RESTService(Logger):
    """
    service accept restful request from users
    """

    def __init__(self, shared_status: _SharedStatus, port: int, host: str = None):
        """
        init rest services instance
        Args:
            shared_status:
            port:
            host:
        """
        self.shared_status = shared_status
        self.port = port
        self.host = host

        self._site: Optional[web.TCPSite] = None

    async def start_rest_site(self):
        """
        start web service non-blocked
        """
        self.info(
            f"starting restful services at {':' if self.host is None else self.host}:{self.port}"
        )
        app = web.Application()
        app.add_routes(self._register_routes())
        runner = web.AppRunner(app, access_log=self.get_logger())
        await runner.setup()
        self._site = web.TCPSite(runner=runner, host=self.host, port=self.port)
        await self._site.start()
        self.info(
            f"restful services started at  {':' if self.host is None else self.host}:{self.port}"
        )

    async def stop_rest_site(self):
        """
        stop web service
        """
        if self._site is not None:
            await self._site.stop()

    def _register_routes(
        self, route_table: Optional[web.RouteTableDef] = None
    ) -> web.RouteTableDef:
        """
        register routes:

            1. submitter
            2. query
        Args:
            route_table: optional provide a `RouteTableDef` instance.

        Returns:

        """
        if route_table is None:
            route_table = web.RouteTableDef()
        route_table.post("/submit")(self._restful_submit)
        route_table.post("/query")(self._restful_query)
        return route_table

    async def _restful_submit(self, request: web.Request) -> web.Response:
        """
        handle submit request
        Args:
            request:

        Returns:

        """
        try:
            data = await request.json()
        except json.JSONDecodeError as e:
            return web.json_response(data={}, status=400, reason=str(e))

        try:
            job_type = data["job_type"]
            job_config = data["job_config"]
            algorithm_config = data.get("algorithm_config", None)
        except KeyError:
            return web.json_response(
                data=dict(exception=traceback.format_exc()), status=400
            )

        # noinspection PyBroadException
        try:
            loader = extensions.get_job_class(job_type)
            validator = extensions.get_job_schema_validator(job_type)
            if loader is None:
                raise FedvisionExtensionException(f"job type {job_type} not supported")
            validator.validate(job_config)
            job_id = self.shared_status.generate_job_id()
            job = loader.load(
                job_id=job_id, config=job_config, algorithm_config=algorithm_config
            )

        except Exception:
            # self.logger.exception("[submit]catch exception")
            reason = traceback.format_exc()
            return web.json_response(data=dict(exception=reason), status=400)

        self.shared_status.job_status[job_id] = _JobStatus.WAITING
        await self.shared_status.job_queue.put(job)

        return web.json_response(
            data={"job_id": job_id},
        )

    async def _restful_query(self, request: web.Request) -> web.Response:
        """
        handle query request

        Args:
            request:

        Returns:

        """
        try:
            data = await request.json()
        except json.JSONDecodeError as e:
            return web.json_response(data={}, status=400, reason=str(e))

        job_id = data.get("job_id", None)
        if job_id is None:
            return web.json_response(data={}, status=400, reason="required `job_id`")

        if job_id not in self.shared_status.job_status:
            return web.json_response(
                data=dict(job_id=job_id, status=str(_JobStatus.NOTFOUND)),
                status=404,
            )

        return web.json_response(
            data=dict(job_id=job_id, status=str(self.shared_status.job_status[job_id])),
        )


class ClusterManagerConnect(Logger):
    """
    cluster manager client
    """

    def __init__(self, address, shared_status: _SharedStatus):
        """
        init cluster manager client
        Args:
            address:
            shared_status:
        """
        self.address = address
        self.shared_status = shared_status
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[cluster_pb2_grpc.ClusterManagerStub] = None

    async def submit_tasks_to_cluster(self):
        """
        infinity loop to get task from queue and submit it to cluster
        """
        while True:
            task = await self.shared_status.cluster_task_queue.get()
            self.debug(
                f"task sending: task_id={task.task_id} task_type={task.task_type} to cluster"
            )
            await self._stub.TaskSubmit(cluster_pb2.TaskSubmit.REQ(task=task))
            self.debug(
                f"task sent: task_id={task.task_id} task_type={task.task_type} to cluster"
            )

    async def task_resource_require(
        self, request: cluster_pb2.TaskResourceRequire.REQ
    ) -> cluster_pb2.TaskResourceRequire.REP:
        """
        acquired resource from cluster(ports)
        Args:
            request:

        Returns:

        """
        response = await self._stub.TaskResourceRequire(request)
        return response

    async def start_cluster_channel(self):
        """
        start channel to cluster manager
        """
        self.info(f"start cluster channel to {self.address}")
        self._channel = grpc.aio.insecure_channel(
            self.address,
            options=[
                ("grpc.max_send_message_length", 512 * 1024 * 1024),
                ("grpc.max_receive_message_length", 512 * 1024 * 1024),
            ],
        )
        self._stub = cluster_pb2_grpc.ClusterManagerStub(self._channel)
        self.info(f"cluster channel started to {self.address}")

    async def cluster_channel_ready(self):
        """
        await until channel ready
        """
        return await self._channel.channel_ready()

    async def stop_cluster_channel(self, grace: Optional[float] = None):
        """
        stop channel to cluster manager
        Args:
            grace:

        Returns:

        """
        self.info(f"stopping cluster channel")
        await self._channel.close(grace)
        self.info(f"cluster channel started to {self.address}")


class Master(Logger):
    def __init__(
        self,
        party_id: str,
        coordinator_address: str,
        cluster_address: str,
        rest_port: int,
        rest_host: str = None,
    ):
        """
          init master

        Args:
            party_id:
            coordinator_address:
            rest_port:
            rest_host:
        """
        self.shared_status = _SharedStatus(party_id=party_id)
        self._coordinator = CoordinatorConnect(
            shared_status=self.shared_status, address=coordinator_address
        )
        self._rest_site = RESTService(
            shared_status=self.shared_status, port=rest_port, host=rest_host
        )
        self._cluster = ClusterManagerConnect(
            shared_status=self.shared_status, address=cluster_address
        )

    async def _submitted_job_handler(self):
        """
        handle submitted jobs.
        """

        async def _co_handler(job: Job):

            # todo: generalize this process
            # stick to paddle fl job now

            # require endpoints before compile start since I don't find a proper way to modify
            # service endpoints after job config generated.
            # really need help hear!

            try:
                if job.resource_required is not None:
                    response = await self._cluster.task_resource_require(
                        job.resource_required
                    )
                    if response.status != cluster_pb2.TaskResourceRequire.SUCCESS:
                        raise Exception(
                            "job failed due to no enough resource"
                        )  # todo: maybe wait some times and retry?
                    job.set_required_resource(response)

                # compile job
                await job.compile()

                # send proposal to coordinator
                self.shared_status.job_status[job.job_id] = _JobStatus.PROPOSAL
                proposal_response = await self._coordinator.make_proposal(
                    job.generate_proposal_request()
                )
                if proposal_response.status != coordinator_pb2.Proposal.SUCCESS:
                    self.debug(
                        f"proposal of job: {job.job_id} failed: {proposal_response.status}"
                    )
                    self.shared_status.job_status[job.job_id] = _JobStatus.FAILED
                    return

                # start local tasks
                self.shared_status.job_status[job.job_id] = _JobStatus.RUNNING
                for task in job.generate_local_tasks():
                    self.debug(
                        f"send local task: {task.task_id} with task type: {task.task_type} to cluster"
                    )
                    await self.shared_status.cluster_task_queue.put(task)
            except Exception as e:
                self.exception(f"run jobs failed: {e}")

        while True:
            submitted_job = await self.shared_status.job_queue.get()
            asyncio.create_task(_co_handler(submitted_job))

    async def start(self):
        """
        start master:

            1. cluster manager to process tasks
            2. restful service to handler request from user
            3. coordinator to connect to `the world`

        """

        # connect to cluster
        await self._cluster.start_cluster_channel()
        while True:
            try:
                await asyncio.wait_for(self._cluster.cluster_channel_ready(), 5)
            except asyncio.TimeoutError:
                self.warning(f"cluster channel not ready, retry in 5 seconds")
            else:
                self.info(f"cluster channel ready!")
                break
        asyncio.create_task(self._cluster.submit_tasks_to_cluster())

        # start rest site
        await self._rest_site.start_rest_site()

        # connect to coordinator
        await self._coordinator.start_coordinator_channel()

        while True:
            try:
                await asyncio.wait_for(self._coordinator.coordinator_channel_ready(), 5)
            except asyncio.TimeoutError:
                self.warning(f"coordinator channel not ready, retry in 5 seconds")
            else:
                self.info(f"coordinator channel ready!")
                break
        asyncio.create_task(self._coordinator.subscribe())

        # job process loop:
        # 1. get job from rest site
        # 2. make proposal to coordinator
        # 3. send task to cluster by put it into a queue
        asyncio.create_task(self._submitted_job_handler())

    async def stop(self):
        """
        stop master
        """
        await self._coordinator.stop_coordinator_channel(grace=1)
        await self._rest_site.stop_rest_site()
        await self._cluster.stop_cluster_channel(grace=1)
