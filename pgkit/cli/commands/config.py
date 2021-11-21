import yaml

import click
from pgkit.application.db import DB
from pgkit.application.utils import get_free_port

@click.group()
def config():
    pass


@config.command()
@click.option('--name', help='Postgres Name', required=True, prompt=True)
@click.option('--version', help='Postgres Version', required=True, prompt=True,
              type=click.Choice(['9.5', '10', '11', '12', '13'], case_sensitive=False))
@click.option('--host', help='Host IP', required=True, prompt=True)
@click.option('--port', help='Port Number', required=True, prompt=True, type=int)
@click.option('--dbname', help='Database Name', required=True, prompt=True)
@click.option('--slot', help='Slot Name', required=True, prompt=True)
@click.option('--username', help='Username', required=True, prompt=True)
@click.option('--password', help='Password', required=True, prompt=True, hide_input=True)
@click.option('--replica-port', help='Replica Port', required=False, prompt=True)
def add(name, version, host, port, dbname, slot, username, password, replica_port):
    if not replica_port:
        replica_port = get_free_port()
    DB.add_config(name, version, host, port, dbname, slot, username, password, replica_port)


@config.command()
@click.argument('name', required=True)
@click.option('--dangerous', help='Dangerous Flag', required=True, is_flag=True)
def remove(name, dangerous):
    if not dangerous:
        return click.echo('Removal requires --dangerous flag.')
    DB.remove_config(name)


@config.command()
@click.argument('name', required=True)
def get(name):
    try:
        return click.echo(yaml.dump(dict(DB.get_config(name))))
    except ValueError as e:
        raise click.BadParameter(message=str(e), param=name, param_hint='NAME')
