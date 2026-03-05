"""
harmonix CLI entry point
"""

import click
from harmonix.scaffold import scaffold_cmd
from harmonix.phi import phi_cmd
from harmonix.status import status_cmd


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    HARMONIX — PSG harmonization pipeline framework.

    Built on Luna for NSRR data harmonization.
    """
    pass


cli.add_command(scaffold_cmd, name="scaffold")
cli.add_command(phi_cmd, name="phi")
cli.add_command(status_cmd, name="status")


if __name__ == "__main__":
    cli()
