import sys

import click

from fedvision import __version__, __basedir__

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    f"{__version__} from {__basedir__} (Python {sys.version[:3]})", "-V", "--version"
)
@click.pass_context
def cli(ctx):
    ...
