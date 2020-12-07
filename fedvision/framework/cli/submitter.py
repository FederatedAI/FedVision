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

import click
import aiohttp
import asyncio
import json

import yaml

from fedvision.framework import extensions


@click.group()
def cli():
    ...


def post(path, json_data):
    async def post_co():
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://127.0.0.1:10002/{path}", json=json_data
            ) as resp:
                if not resp.ok:
                    print(resp.status)
                    resp.raise_for_status()
                else:
                    print(json.dumps(await resp.json(), indent=2))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(post_co())


@cli.command()
@click.option("--config", type=click.File(), required=True)
def submit(config):
    config_json = yaml.safe_load(config)
    job_type = config_json.get("job_type")
    job_config = config_json.get("job_config")
    extensions.get_job_schema_validator(job_type).validate(job_config)
    post("submit", dict(job_type=job_type, job_config=job_config))


if __name__ == "__main__":
    cli()
