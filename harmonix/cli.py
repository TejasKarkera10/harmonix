"""
harmonix CLI entry point
"""

import click
from harmonix.scaffold import scaffold_cmd


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    HARMONIX — PSG harmonization pipeline framework.

    Built on Luna for NSRR data harmonization.
    """
    pass


cli.add_command(scaffold_cmd, name="scaffold")


if __name__ == "__main__":
    cli()
