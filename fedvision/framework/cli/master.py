import asyncio

import click


@click.command()
@click.option("--party-id", type=str, required=True, help="party id")
@click.option("--submitter-port", type=int, required=True, help="submitter port")
@click.option(
    "--cluster-address", type=str, required=True, help="cluster manager address"
)
@click.option(
    "--coordinator-address", type=str, required=True, help="coordinator address"
)
def start_master(party_id, submitter_port, cluster_address, coordinator_address):
    """
    start master
    """
    from fedvision.framework.utils import logger

    logger.set_logger(f"master-{party_id}")
    from fedvision.framework.master.master import Master

    loop = asyncio.get_event_loop()
    master = Master(
        party_id=party_id,
        coordinator_address=coordinator_address,
        cluster_address=cluster_address,
        rest_port=submitter_port,
    )
    try:
        loop.run_until_complete(master.start())
        click.echo(f"master started")
        loop.run_forever()
    except KeyboardInterrupt:
        click.echo("keyboard interrupted")
    finally:
        loop.run_until_complete(master.stop())
        click.echo(f"master stop")
        loop.close()


if __name__ == "__main__":
    start_master()
