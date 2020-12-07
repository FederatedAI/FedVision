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

import asyncio

import click


@click.command(name="start-worker")
@click.option("--name", type=str, required=True, help="worker name")
@click.option("--worker-ip", type=str, required=True, help="worker ip")
@click.option("--max-tasks", type=int, required=True, help="max tasks")
@click.option("--port-start", type=int, required=True, help="port start")
@click.option("--port-end", type=int, required=True, help="port end")
@click.option(
    "--manager-address", type=str, required=True, help="cluster manager address"
)
def start_worker(name, worker_ip, max_tasks, manager_address, port_start, port_end):
    """
    start worker
    """
    from fedvision.framework.utils import logger

    logger.set_logger(f"worker-{worker_ip}")
    from fedvision.framework.cluster.worker import ClusterWorker

    loop = asyncio.get_event_loop()
    worker = ClusterWorker(
        worker_id=name,
        worker_ip=worker_ip,
        max_tasks=max_tasks,
        manager_address=manager_address,
        port_start=port_start,
        port_end=port_end,
    )
    try:
        loop.run_until_complete(worker.start())
        click.echo(f"worker {name} start")
        loop.run_until_complete(worker.wait_for_termination())
    except KeyboardInterrupt:
        click.echo("keyboard interrupted")
    finally:
        loop.run_until_complete(worker.stop())
        loop.run_until_complete(asyncio.sleep(1))
        loop.close()
        click.echo(f"worker {name} stop")


if __name__ == "__main__":
    start_worker()
