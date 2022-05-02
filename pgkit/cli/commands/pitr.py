from datetime import datetime, timedelta

import click
from dateutil.parser import parse as parse_date
from pytz import timezone
import pgkit.application.pg as PG
from pgkit.application.db import DB


@click.group()
def pitr():
    pass


@pitr.command()
@click.argument('name', required=True)
@click.argument('delay', required=True, type=int)
def backup(name, delay):
    config = DB.get_config(name)
    PG.backup(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
        config.get('use_separate_receivewal_service', False),
        replica_delay=delay
    )


@pitr.command()
@click.argument('name', required=True)
def status(name):
    config = DB.get_config(name)
    PG.print_status(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
    )


@pitr.command()
@click.argument('name', required=True)
@click.argument('target_time', required=True)
def recover(name, target_time):
    config = DB.get_config(name)
    if target_time != 'latest':
        try:
            parsed_target_date = parse_date(target_time)
            target_time = str(timezone('Asia/Tehran').localize(parsed_target_date))
        except ValueError:
            return click.echo('target_time argument should have a valid datetime format.')
    PG.recovery(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
        time_to_recover=target_time
    )


@pitr.command()
@click.argument('name', required=True)
def promote(name):
    config = DB.get_config(name)
    PG.promote(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
    )


@pitr.command()
@click.argument('name', required=True)
@click.argument('delay', required=True, type=float)
def status(name, delay):
    target_time = (datetime.today() - timedelta(hours=4.5)).strftime('%Y-%m-%d %H:%M:%S GMT')
    print(f'TARGET TIME: {target_time}')
    if click.confirm('Do you want to continue?'):
        time_to_recover = datetime.today() - timedelta(hours=delay)
        config = DB.get_config(name)
        PG.print_status(
            config['name'],
            config['host'],
            config['port'],
            config['version'],
            config['dbname'],
            config['username'],
            config['password'],
            config['slot'],
            config['replica_port'],
        )
