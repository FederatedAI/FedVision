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

import urllib.parse
from pathlib import Path

import click
import aiohttp
import asyncio
import json

import yaml

from fedvision.framework import extensions


@click.group()
def cli():
    ...


def post(endpoint, path, json_data):
    async def post_co():
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=urllib.parse.urljoin(f"http://{endpoint}", path), json=json_data
            ) as resp:
                if not resp.ok:
                    print(resp.status)
                    resp.raise_for_status()
                else:
                    print(json.dumps(await resp.json(), indent=2))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(post_co())


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "--endpoint",
    type=str,
    required=True,
)
def submit(endpoint, config):

    base = Path(config)
    with base.open("r") as f:
        config_json = yaml.load(f, yaml.Loader)
    job_type = config_json.get("job_type")
    job_config = config_json.get("job_config")
    algorithm_config_path = base.parent.joinpath(
        config_json.get("algorithm_config")
    ).absolute()
    with algorithm_config_path.open("r") as f:
        algorithm_config_string = f.read()

    extensions.get_job_schema_validator(job_type).validate(job_config)
    post(
        endpoint,
        "submit",
        dict(
            job_type=job_type,
            job_config=job_config,
            algorithm_config=algorithm_config_string,
        ),
    )


if __name__ == "__main__":
    cli()
