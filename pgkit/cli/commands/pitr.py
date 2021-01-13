import click
from pgkit.application.db import DB
import pgkit.application.pitr as PITR


@click.group()
def pitr():
    pass


@pitr.command()
@click.argument('name', required=True)
@click.argument('delay', required=True, type=int)
def backup(name, delay):
    config = DB.get_config(name)
    print(config)
    PITR.backup(**{**config, 'replica_delay': delay})


@pitr.command()
def restore():
    pass


@pitr.command()
def status():
    pass
