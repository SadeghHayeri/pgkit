import click
from pgkit.application.db import DB
from pgkit.application.models import Master, Replica
import pgkit.application.pg as PG


@click.command()
@click.argument('name', required=True)
@click.option('--replica', is_flag=True, default=False)
def shell(name, replica):
    config = DB.get_config(name)
    PG.shell(**config, shell_to_replica=replica)
