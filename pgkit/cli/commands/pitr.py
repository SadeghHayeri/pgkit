import click
from pgkit.application.db import DB
import pgkit.application.pg as PG
from datetime import datetime, timedelta

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


@pitr.command()
@click.argument('name', required=True)
@click.argument('delay', required=True, type=float)
def status(name, delay):
    target_time = (datetime.today() - timedelta(hours=4.5)).strftime('%Y-%m-%d %H:%M:%S GMT')
    print(f'TARGET TIME: {target_time}')
    if click.confirm('Do you want to continue?'):
        time_to_recover = datetime.today() - timedelta(hours=delay)
        config = DB.get_config(name)
        PG.print_status(**config, time_to_recover)

