import click
from pgkit.application.db import DB

@click.group()
def config():
    pass

@config.command()
@click.option('--name', help='Postgres Name', required=True, prompt=True)
@click.option('--version', help='Postgres Version', required=True, prompt=True, type=click.Choice(['9.5', '10', '11', '12', '13'], case_sensitive=False))
@click.option('--host', help='Host IP', required=True, prompt=True)
@click.option('--port', help='Port Number', required=True, prompt=True, type=int)
@click.option('--slot', help='Slot Name', required=True, prompt=True)
@click.option('--username', help='Username', required=True, prompt=True)
@click.option('--password', help='Username', required=True, prompt=True, hide_input=True)
def add(name, version, host, port, slot, username, password):
    DB.add_config(name, version, host, port, slot, username, password)

@config.command()
@click.argument('name', required=True)
@click.option('--dangerous', help='Dangerous Flag', required=True, is_flag=True)
def remove(name, dangerous):
    if not dangerous:
        return click.echo('Removal requires --dangerous flag.')
    DB.remove_config(name)
