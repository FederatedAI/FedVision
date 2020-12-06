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
