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
    PG.backup(**{**config, 'replica_delay': delay})


@pitr.command()
@click.argument('name', required=True)
def status(name):
    config = DB.get_config(name)
    PG.print_status(**config)


@pitr.command()
@click.argument('name', required=True)
@click.argument('target_time', required=True)
def recover(name, target_time):
    config = DB.get_config(name)
    try:
        parsed_target_date = parse_date(target_time)
        date_str = str(timezone('Asia/Tehran').localize(parsed_target_date))
        PG.recovery(**config, time_to_recover=date_str)
    except ValueError:
        return click.echo('target_time argument should have a valid datetime format.')


@pitr.command()
@click.argument('name', required=True)
@click.argument('output_path', required=True)
@click.option('--compress', required=False, is_flag=True)
@click.option('--compression-level', required=False, type=click.Choice(list(map(str, range(1, 10)))))
def dump(name, output_path, compress, compression_level):
    if not compress and compression_level:
        return click.echo('--compress flag should be given when compression level is specified')
    config = DB.get_config(name)
    PG.dump(**config, output_path=output_path, compress=compress, compression_level=compression_level)


@pitr.command()
@click.argument('name', required=True)
@click.argument('delay', required=True, type=float)
def status(name, delay):
    target_time = (datetime.today() - timedelta(hours=4.5)).strftime('%Y-%m-%d %H:%M:%S GMT')
    print(f'TARGET TIME: {target_time}')
    if click.confirm('Do you want to continue?'):
        time_to_recover = datetime.today() - timedelta(hours=delay)
        config = DB.get_config(name)
        PG.print_status(**config)
