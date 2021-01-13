from pgkit.application.utils import execute, execute_sync
from jinja2 import Template
from pathlib import Path
from time import sleep

def backup(name, host, port, version, username, password, slot, delay):
    backup_destination = '/var/lib/postgresql/{}/{}'.format(version, name)
    wal_destination = '/var/lib/postgresql/wals/{}'.format(name)

    create_postgres_database(name, version)
    stop_postgres(name, version)
    remove_initial_database(backup_destination)
    setup_receive_wal_service(name, host, port, version, username, password, slot, wal_destination)
    print('Sleep 10s to get wal files'); sleep(1)
    take_basebackup(name, host, port, version, username, password, backup_destination)
    config_recovery_file(name, host, port, version, username, password, backup_destination, wal_destination, slot, delay)
    start_postgres(name, version)

def create_postgres_database(name, version):
    print('Creat postgres database')
    execute_sync('pg_createcluster {} {}'.format(version, name))

def start_postgres(name, version):
    print('Start postgres')
    execute_sync('pg_ctlcluster {} {} start'.format(version, name))

def stop_postgres(name, version):
    print('Stop postgres')
    execute_sync('pg_ctlcluster {} {} stop'.format(version, name))

def remove_initial_database(destination):
    print('Remove initial database files')
    execute_sync('rm -rf {}'.format(destination))

def setup_receive_wal_service(name, host, port, version, username, password, slot, destination):
    template_path = Path(__file__).parent / "./templates/wal-receive-service.service"
    with open(template_path) as file_:
        template = Template(file_.read())

    print('Create wal folder')
    execute_sync('mkdir {}'.format(destination))
    execute_sync('chown -R postgres:postgres {}'.format(destination))

    service = template.render(
        name=name,
        version=version,
        host=host,
        port=port,
        username=username,
        password=password,
        slot=slot,
        destination=destination
    )

    print('Create wal-receive service')
    f = open('/etc/systemd/system/receivewal-{}-{}.service'.format(version, name), "w")
    f.write(service)
    f.close()

    print('Reload systemctl')
    execute_sync('systemctl daemon-reload')
    print('Run wal-receive service')
    execute_sync('service receivewal-{}-{} start'.format(version, name))

def take_basebackup(name, host, port, version, username, password, destination):
    command = '/usr/lib/postgresql/{version}/bin/pg_basebackup' \
              ' -h {host}' \
              ' -p {port}' \
              ' -D {destination}' \
              ' -U {username}' \
              ' -v --checkpoint=fast'.format(
        host=host,
        port=port,
        version=version,
        username=username,
        password=password,
        destination=destination,
    )
    print('Take basebackup')
    execute_sync(command, env=[('PGPASSWORD', password)])

    print('change owner to postgres')
    execute_sync('chown -R postgres:postgres {}'.format(destination))


def config_recovery_file(name, host, port, version, username, password, base_destination, wal_destination, slot, delay):
    template_path = Path(__file__).parent / "./templates/{}-recovery.conf".format(version)
    with open(template_path) as file_:
        template = Template(file_.read())

    standby_port = execute_sync("pg_lsclusters | grep {} | awk '{ print $3 }'".format(name))

    recovery_config = template.render(
        name=name,
        host=host,
        port=port,
        version=version,
        username=username,
        password=password,
        base_destination=base_destination,
        wal_destination=wal_destination,
        slot=slot,
        delay=delay,
        dbname='postgres',
        standby_mode='true',
        standby_port=standby_port,
    )

    print('Create recovery.conf file')
    if version == '12':
        f = open('/etc/postgresql/12/{}/postgresql.conf'.format(name), "w")
    else:
        f = open('{}/recovery.conf'.format(base_destination), "w")
    f.write(recovery_config)
    f.close()

    execute_sync('chown -R postgres:postgres {}/recovery.conf'.format(base_destination))
