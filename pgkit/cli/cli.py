import click
from pgkit.cli.commands.config import config
from pgkit.cli.commands.pitr import pitr
from pgkit.cli.commands.status import status
from pgkit.cli.commands.shellx import shell, dumpall, dump, stop, restart, start, list


@click.group()
def cli():
    pass


def main():
    cli.add_command(config)
    cli.add_command(pitr)
    cli.add_command(status)
    cli.add_command(list)
    cli.add_command(shell)
    cli.add_command(dump)
    cli.add_command(dumpall)
    cli.add_command(start)
    cli.add_command(stop)
    cli.add_command(restart)
    cli()
