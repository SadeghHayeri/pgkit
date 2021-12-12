import shutil
from pathlib import Path
from time import sleep

from jinja2 import Template

from pgkit.application.models import Postgres
from pgkit.application.utils import *
from pgkit.application.db import DB


class Replica(Postgres):
    def __init__(self, master, port, delay):
        super().__init__(name=master.name,
                         host='localhost',
                         port=port,
                         dbname='postgres',
                         version=master.version,
                         username='postgres',
                         password=None,
                         slot=None)
        self.master = master
        self.delay = delay
        self.db_location = f'/var/lib/postgresql/{self.version}/{self.name}'
        self.config_location = f'/etc/postgresql/{self.version}/{self.name}'
        self.wal_location = f'/var/lib/postgresql/wals/{self.version}/{self.name}'

    def start_backup(self):
        self.stop()
        self.remove_related_directories()
        self.create_cluster()
        self.stop()
        self.remove_db_directory()
        self.stop_wal_receive_service()
        self.drop_replication_slot()
        self.create_replication_slot()
        self.setup_wal_receive_service()
        self.master.force_switch_wal()
        sleep(10)  # time to receive first wal segments
        self.create_base_backup()
        self.configure_recovery_file()
        self.start()

    def create_cluster(self):
        execute_sync(f'pg_createcluster {self.version} {self.name} -p {self.port}')

    def stop(self):
        execute_sync(f'pg_ctlcluster {self.version} {self.name} stop')

    def start(self):
        execute_sync(f'pg_ctlcluster {self.version} {self.name} start')

    def restart(self):
        execute_sync(f'pg_ctlcluster {self.version} {self.name} restart')

    def remove_db_directory(self):
        execute_sync(f'rm -rf {self.db_location}')

    def remove_config_directory(self):
        execute_sync(f'rm -rf {self.config_location}')

    def remove_existing_wal_files(self):
        execute_sync(f'rm -rf {self.wal_location}')

    def create_replication_slot(self):
        self.master.create_replication_slot()

    def drop_replication_slot(self):
        self.master.drop_replication_slot()

    def stop_wal_receive_service(self):
        stop_service(f'receivewal-{self.version}-{self.name}')

    def remove_related_directories(self):
        self.remove_db_directory()
        self.remove_config_directory()
        self.remove_existing_wal_files()

    def _stop_old_wal_receive_service(self):
        try:
            stop_service(f'receivewal-{self.version}-{self.name}')
        except:
            pass

    def setup_wal_receive_service(self):
        self._stop_old_wal_receive_service()

        template_path = Path(__file__).parent / "../templates/wal-receive-service.service"
        template = Template(read_file(template_path))

        print('Create wal folder')
        create_directory(self.wal_location)

        print('Create wal-receive service')
        service_file = template.render(
            name=self.name,
            version=self.version,
            host=self.master.host,
            port=self.master.port,
            username=self.master.username,
            password=self.master.password,
            slot=self.master.slot,
            destination=self.wal_location
        )
        write_file(f'/etc/systemd/system/receivewal-{self.version}-{self.name}.service', service_file)

        print('Run wal-receive service')
        restart_service(f'receivewal-{self.version}-{self.name}', reload_systemctl=True)

    def create_base_backup(self):
        print('Take basebackup')
        command = f'/usr/lib/postgresql/{self.version}/bin/pg_basebackup' \
                  f' -h {self.master.host}' \
                  f' -p {self.master.port}' \
                  f' -D {self.db_location}' \
                  f' -U {self.master.username}' \
                  f' -v --checkpoint=fast --progress'
        if self.version >= 10:
            command += ' --wal-method=none'
        execute_sync(command, env=[('PGPASSWORD', self.master.password)])

        print('change owner to postgres')
        chown(self.db_location, 'postgres')

    def recovery(self, target_time):
        self.configure_recovery_file(recovery=True, recovery_target_time=target_time)
        self._rename_partial_wal_file()
        self.restart()

    def get_config_parameter_value(self, parameter):
        try:
            print(f'Getting config parameter {parameter} from master')
            param_val = self.master.get_config_parameter_value(parameter)
            DB.update_config(self.name, {parameter: param_val})
        except Exception as e:
            print('Error getting master parameter value:', e)
            print('Using DB value')
            param_val = DB.get_config(self.name)[parameter]
        return param_val

    def configure_recovery_file(self, recovery=False, recovery_target_time=None):
        template_path = Path(__file__).parent / "../templates/{}-recovery.conf".format(self.version)
        template = Template(read_file(template_path))
        latest = recovery_target_time == 'latest'

        max_connections = self.get_config_parameter_value('max_connections')
        max_worker_processes = self.get_config_parameter_value('max_worker_processes')

        print('Create recovery.conf file')
        recovery_config = template.render(
            name=self.name,
            host=self.master.host,
            port=self.master.port,
            version=self.version,
            username=self.master.username,
            password=self.master.password,
            base_destination=self.db_location,
            wal_destination=self.wal_location,
            slot=self.master.slot,
            delay=self.delay,
            dbname='postgres',
            standby_mode='true',
            standby_port=self.port,
            recovery_mode=recovery,
            recovery_target_time=recovery_target_time,
            latest=latest,
            max_connections=max_connections,
            max_worker_processes=max_worker_processes,
        )

        file_location = f'/etc/postgresql/{self.version}/{self.name}/postgresql.conf' if self.version >= 12 \
            else f'{self.db_location}/recovery.conf'

        write_file(file_location, recovery_config)
        chown(file_location, 'postgres')

        if self.version >= 12:
            touch_file(f'{self.db_location}/recovery.signal')
            touch_file(f'{self.db_location}/standby.signal')

    def dump(self, database_name, output_path, compress=False, compression_level=9):
        if compress:
            execute_sync(
                f'runuser -l postgres'
                f' -c \'/usr/lib/postgresql/{self.version}/bin/pg_dump'
                f' --no-owner'
                f' -p {self.port}'
                f' -U postgres'
                f' -d {database_name}'
                f' | gzip -{compression_level} > {output_path}\''
            )
        else:
            execute_sync(
                f'runuser -l postgres'
                f' -c \'/usr/lib/postgresql/{self.version}/bin/pg_dump'
                f' -f {output_path}'
                f' --no-owner'
                f' -p {self.port}'
                f' -U postgres'
                f' -d {database_name}\''
            )

    def dumpall(self, output_path, compress=False, compression_level=9):
        if compress:
            execute_sync(
                f'runuser -l postgres '
                f'-c \'/usr/lib/postgresql/{self.version}/bin/pg_dumpall'
                f' --no-owner'
                f' -p {self.port}'
                f' -U postgres'
                f' | gzip -{compression_level} > {output_path}\''
            )
        else:
            execute_sync(
                f'runuser -l postgres'
                f' -c \'/usr/lib/postgresql/{self.version}/bin/pg_dumpall'
                f' -f {output_path}'
                f' --no-owner'
                f' -p {self.port}'
                f' -U postgres\''
            )

    def shell(self):
        execute_sync(f'runuser -l postgres -c \'psql -p {self.port}\'', no_pipe=True)

    def promote(self):
        execute_sync(
            f'pg_ctlcluster {self.version} {self.name} promote'
        )
        self.restart()

    def _rename_partial_wal_file(self):
        wal_location_contents = os.listdir(self.wal_location)
        for filename in wal_location_contents:
            if filename.endswith('.partial'):
                destination_path = os.path.join(self.wal_location, removesuffix(filename, '.partial'))
                shutil.copy2(
                    os.path.join(self.wal_location, filename),
                    destination_path,
                )
                chown(destination_path, 'postgres')

    def _get_current_delay(self):
        file_location = f'/etc/postgresql/{self.version}/{self.name}/postgresql.conf' if self.version >= 12 \
            else f'{self.db_location}/recovery.conf'

        config = read_file(file_location)
        for line in config.split('\n'):
            if 'recovery_min_apply_delay' in line:
                return int(line.split(' ')[2]) / 3600000

    def _get_replication_slot_status(self):
        return self.master.run_cmd('select active from pg_replication_slots')

    def _get_postgres_logs(self, lines):
        return execute_sync(f'tail -n {lines} /var/log/postgresql/postgresql-{self.version}-{self.name}.log')

    def _get_receive_wal_logs(self, lines):
        return execute_sync(f'tail -n {lines} /var/log/postgresql/receivewal-{self.version}-{self.name}.log')

    def print_status(self):
        print(f'# DELAY: {self._get_current_delay()}h')
        print()
        print('# REPLICATION SLOT:')
        print(self._get_replication_slot_status())
        print()
        print('# POSTGRES REPLICA SERVICE:')
        print(get_service_status(f'postgresql@{self.version}-{self.name}'))
        print()
        print('# RECEIVE WAL SERVICE:')
        print(get_service_status(f'receivewal-{self.version}-{self.name}'))
        print()
        print('# POSTGRES LOGS:')
        print(self._get_postgres_logs(10))
        print()
        print('# RECEIVE WAL LOGS:')
        print(self._get_receive_wal_logs(10))
