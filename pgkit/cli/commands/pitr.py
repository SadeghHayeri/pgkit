import click
from pgkit.application.db import DB
import pgkit.application.pg as PG


@click.group()
def pitr():
    pass


@pitr.command()
@click.argument('name', required=True)
@click.argument('delay', required=True, type=int)
def backup(name, delay):
    config = DB.get_config(name)
    PG.backup(**{**config, 'replica_delay': delay})


@pitr.command()
def restore():
    pass

@pitr.command()
@click.argument('name', required=True)
def status(name):
    config = DB.get_config(name)
    PG.print_status(**config)

