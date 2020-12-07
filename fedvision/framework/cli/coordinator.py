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


@click.command()
@click.option("-p", "--port", type=int, required=True, help="port")
def start_coordinator(port):
    """
    start coordinator
    """
    from fedvision.framework.utils import logger

    logger.set_logger("coordinator")
    from fedvision.framework.coordinator.coordinator import Coordinator

    loop = asyncio.get_event_loop()
    coordinator = Coordinator(port)
    try:
        loop.run_until_complete(coordinator.start())
        click.echo(f"coordinator server start at port:{port}")
        loop.run_forever()
    except KeyboardInterrupt:
        click.echo("keyboard interrupted")
    finally:
        loop.run_until_complete(coordinator.stop())
        click.echo(f"coordinator server stop")
        loop.close()


if __name__ == "__main__":
    start_coordinator()
