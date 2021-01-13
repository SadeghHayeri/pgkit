import click
from pgkit.cli.commands.config import config
from pgkit.cli.commands.pitr import pitr
from pgkit.cli.commands.status import status
from pgkit.cli.commands.list import list

@click.group()
def cli():
    pass

def main():
    cli.add_command(config)
    cli.add_command(pitr)
    cli.add_command(status)
    cli.add_command(list)
    cli()
