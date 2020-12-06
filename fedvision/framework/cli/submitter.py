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
