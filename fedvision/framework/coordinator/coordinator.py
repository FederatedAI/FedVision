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
import random
import time
from typing import Optional, MutableMapping, MutableSet, List, AsyncGenerator

import attr
import grpc

from fedvision.framework.protobuf import coordinator_pb2_grpc, coordinator_pb2, job_pb2
from fedvision.framework.utils.logger import Logger


@attr.s
class _TaskProviderForEnrolledParty(object):
    def __attrs_post_init__(self):
        self.queue: asyncio.Queue[_Proposal] = asyncio.Queue()
        self.closed = False


@attr.s
class _Proposal(object):
    uid = attr.ib(type=str)
    job_type = attr.ib(type=str)
    tasks = attr.ib(type=List[job_pb2.Task])
    deadline = attr.ib(type=int)
    minimum_acceptance = attr.ib(type=int)
    maximum_acceptance = attr.ib(type=int)
    goal_reached = attr.ib(type=bool, default=False)

    def __attrs_post_init__(self):
        self.responders = set()
        self.open_period_finished = asyncio.Event()
        self.chosen = {}

    @classmethod
    def from_pb(cls, uid, pb: coordinator_pb2.Proposal.REQ):
        return _Proposal(
            uid=uid,
            job_type=pb.job_type,
            tasks=pb.tasks,
            deadline=time.time() + pb.proposal_wait_time,
            minimum_acceptance=pb.minimum_acceptance,
            maximum_acceptance=pb.maximum_acceptance,
        )

    def has_enough_responders(self):
        return self.minimum_acceptance <= len(self.responders)

    def add_responders(self, party_id):
        self.responders.add(party_id)

    def set_open_period_finished(self, goal_reached):
        self.goal_reached = goal_reached
        if len(self.responders) > self.maximum_acceptance:
            for i, responder in enumerate(
                random.choices(list(self.responders), k=self.maximum_acceptance)
            ):
                self.chosen[responder] = self.tasks[i]
        else:
            for i, responder in enumerate(list(self.responders)):
                self.chosen[responder] = self.tasks[i]
        self.open_period_finished.set()


class Coordinator(Logger, coordinator_pb2_grpc.CoordinatorServicer):
    def __init__(self, port: int):
        """
        init coordinator

        Args:
            port: coordinator serving port
        """
        self._serving = True
        self._enrolled: MutableMapping[str, _TaskProviderForEnrolledParty] = {}
        self._proposals: MutableMapping[str, _Proposal] = {}
        self._job_type_to_subscribes: MutableMapping[str, MutableSet[str]] = {}
        self._check_interval = 0.5
        self._count_id = 0

        self._grpc_port = port
        self._grpc_server = None

    async def start(self):
        self.info(f"starting grpc server")
        self._grpc_server = grpc.aio.server(
            options=[
                ("grpc.max_send_message_length", 512 * 1024 * 1024),
                ("grpc.max_receive_message_length", 512 * 1024 * 1024),
            ]
        )
        coordinator_pb2_grpc.add_CoordinatorServicer_to_server(self, self._grpc_server)
        self._grpc_server.add_insecure_port(f"[::]:{self._grpc_port}")
        await self._grpc_server.start()
        self.info(f"grpc server started at port {self._grpc_port}")

    async def stop(self):
        self.info(f"stopping grpc server gracefully")
        await self._grpc_server.stop(1)
        self.info(f"grpc server stopped")

    async def wait_for_termination(self, timeout: Optional[float] = None):
        await self._grpc_server.wait_for_termination(timeout=timeout)

    async def Leave(self, request, context):
        if request.party_id not in self._enrolled:
            return coordinator_pb2.Leave.REP(status=coordinator_pb2.Leave.NOT_FOUND)
        self._enrolled[request.party_id].closed = True
        await self._enrolled[request.party_id].queue.join()
        self._enrolled.__delitem__(request.party_id)
        return coordinator_pb2.Leave.REP(status=coordinator_pb2.Leave.SUCCESS)

    # @stream_grpc_logging_decorator
    async def Subscribe(
        self, request: coordinator_pb2.Subscribe.REQ, context: grpc.aio.ServicerContext
    ) -> AsyncGenerator[coordinator_pb2.Subscribe.REP, None]:
        """
        handle subscribe gRPC request, response job proposals in stream

        Args:
            request:
            context:

        Returns:

        """
        if request.party_id in self._enrolled:
            yield coordinator_pb2.Subscribe.REP(
                status=coordinator_pb2.Subscribe.DUPLICATE_ENROLL
            )
            return
        if not self._serving:
            yield coordinator_pb2.Subscribe.REP(
                status=coordinator_pb2.Subscribe.NOT_SERVING
            )
            return

        task_provider = _TaskProviderForEnrolledParty()
        self._enrolled[request.party_id] = task_provider

        for job_type in request.job_types:
            self._job_type_to_subscribes.setdefault(job_type, set()).add(
                request.party_id
            )

        while True:
            if task_provider.closed:
                break

            try:
                # make stop subscribe passable, check status regularly
                proposal = await asyncio.wait_for(
                    task_provider.queue.get(), timeout=self._check_interval
                )
            except asyncio.TimeoutError:
                # not receive proposal task for a while, maybe:
                # 1. just no new proposal
                # 2. flag has changed to false and no new proposal will in-queue
                continue
            else:
                yield coordinator_pb2.Subscribe.REP(
                    status=coordinator_pb2.Subscribe.SUCCESS,
                    proposal_id=proposal.uid,
                    job_type=proposal.job_type,
                )
                task_provider.queue.task_done()

        # clean proposals
        while not task_provider.queue.empty():
            await task_provider.queue.get()
            task_provider.queue.task_done()

    async def Proposal(
        self, request: coordinator_pb2.Proposal.REQ, context: grpc.aio.ServicerContext
    ) -> coordinator_pb2.Proposal.REP:
        """
        handle job proposal gRPC request

        Args:
            request:
            context:

        Returns:

        """

        uid = self._generate_proposal_id(request.job_id)
        proposal = _Proposal.from_pb(uid=uid, pb=request)
        self._proposals[uid] = proposal

        if proposal.job_type not in self._job_type_to_subscribes:
            self.info(
                f"job type {proposal.job_type} not in {self._job_type_to_subscribes}, reject"
            )
            return coordinator_pb2.Proposal.REP(status=coordinator_pb2.Proposal.REJECT)

        if (
            len(self._job_type_to_subscribes[proposal.job_type])
            < proposal.minimum_acceptance
        ):
            self.info(
                f"not enough parties alive accept job type {proposal.job_type},"
                f" required {proposal.minimum_acceptance}, "
                f"{len(self._job_type_to_subscribes[proposal.job_type])} alive"
            )
            return coordinator_pb2.Proposal.REP(
                status=coordinator_pb2.Proposal.NOT_ENOUGH_SUBSCRIBERS
            )

        # dispatch proposal
        for party_id in self._job_type_to_subscribes[proposal.job_type]:
            await self._enrolled[party_id].queue.put(proposal)

        # sleep until timeout and then check if there are enough responders
        await asyncio.sleep(request.proposal_wait_time)
        if not proposal.has_enough_responders():
            proposal.set_open_period_finished(goal_reached=False)
            return coordinator_pb2.Proposal.REP(
                status=coordinator_pb2.Proposal.NOT_ENOUGH_RESPONDERS
            )

        proposal.set_open_period_finished(goal_reached=True)
        return coordinator_pb2.Proposal.REP(status=coordinator_pb2.Proposal.SUCCESS)

    async def FetchTask(
        self, request: coordinator_pb2.FetchTask.REQ, context: grpc.aio.ServicerContext
    ) -> coordinator_pb2.Proposal.REP:
        """
        handle task fetch gRPC request

        Args:
            request:
            context:

        Returns:

        """

        if request.proposal_id not in self._proposals:
            return coordinator_pb2.FetchTask.REP(
                status=coordinator_pb2.FetchTask.NOT_FOUND
            )

        if request.party_id not in self._enrolled:
            return coordinator_pb2.FetchTask.REP(
                status=coordinator_pb2.FetchTask.NOT_ALLOW
            )

        proposal = self._proposals[request.proposal_id]

        if proposal.open_period_finished.is_set():
            return coordinator_pb2.FetchTask.REP(
                status=coordinator_pb2.FetchTask.TIMEOUT
            )

        proposal.add_responders(request.party_id)
        await proposal.open_period_finished.wait()

        if not proposal.goal_reached:
            return coordinator_pb2.FetchTask.REP(
                status=coordinator_pb2.FetchTask.CANCELED
            )

        self.info(f"chosen: {proposal.chosen.keys()}")
        if request.party_id not in proposal.chosen:
            return coordinator_pb2.FetchTask.REP(
                status=coordinator_pb2.FetchTask.RANDOM_OUT
            )

        # accepted, finally!
        success_rep = coordinator_pb2.FetchTask.REP(
            status=coordinator_pb2.FetchTask.READY,
            task=proposal.chosen[request.party_id],
        )
        return success_rep

    def _generate_proposal_id(self, name):
        self._count_id += 1
        return f"{name}-coo_{self._count_id}"
