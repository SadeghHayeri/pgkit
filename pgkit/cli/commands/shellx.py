import yaml

import click
from pgkit.application.db import DB
import pgkit.application.pg as PG


@click.command()
@click.argument('name', required=True)
@click.option('--replica', is_flag=True, default=False)
def shell(name, replica):
    config = DB.get_config(name)
    PG.shell(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
        shell_to_replica=replica
    )


@click.command()
@click.argument('name', required=True)
@click.argument('database_name', required=True)
@click.argument('output_path', required=True)
@click.option('--compress', required=False, is_flag=True)
@click.option('--compression-level', required=False, type=click.Choice(list(map(str, range(1, 10)))))
def dump(name, database_name, output_path, compress, compression_level):
    if not compress and compression_level:
        return click.echo('--compress flag should be given when compression level is specified')
    config = DB.get_config(name)
    PG.dump(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
        database_name=database_name,
        output_path=output_path,
        compress=compress,
        compression_level=compression_level
    )


@click.command()
@click.argument('name', required=True)
@click.argument('output_path', required=True)
@click.option('--compress', required=False, is_flag=True)
@click.option('--compression-level', required=False, type=click.Choice(list(map(str, range(1, 10)))))
def dumpall(name, output_path, compress, compression_level):
    if not compress and compression_level:
        return click.echo('--compress flag should be given when compression level is specified')
    config = DB.get_config(name)
    PG.dumpall(
        config['name'],
        config['host'],
        config['port'],
        config['version'],
        config['dbname'],
        config['username'],
        config['password'],
        config['slot'],
        config['replica_port'],
        output_path=output_path,
        compress=compress,
        compression_level=compression_level
    )


@click.command()
@click.argument('name', required=True)
def stop(name):
    config = DB.get_config(name)
    PG.stop(
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


@click.command()
@click.argument('name', required=True)
def start(name):
    config = DB.get_config(name)
    PG.start(
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


@click.command()
@click.argument('name', required=True)
def restart(name):
    config = DB.get_config(name)
    PG.restart(
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


@click.command()
def list():
    return click.echo(yaml.dump(DB.get_configs_list()))
