from pgkit.application.models import Postgres
from pgkit.application.utils import *
from jinja2 import Template
from pathlib import Path
from time import sleep


class Replica(Postgres):
    def __init__(self, master, port, delay):
        super().__init__(name=master.name,
                         host='localhost',
                         port=port,
                         version=master.version,
                         username='postgres',
                         password=None,
                         slot=None)
        self.master = master
        self.delay = delay
        self.db_location = '/var/lib/postgresql/{}/{}'.format(self.version, self.name)
        self.wal_location = '/var/lib/postgresql/wals/{}/{}'.format(self.version, self.name)

    def start_backup(self):
        self.create_cluster()
        self.stop()
        self.remove_db_directory()
        self.setup_wal_receive_service()
        self.master.force_switch_wal()
        sleep(10)  # time to receive first wal segments
        self.configure_recovery_file()
        self.start()

    def create_cluster(self):
        execute_sync('pg_createcluster {} {}'.format(self.version, self.name))

    def stop(self):
        execute_sync('pg_ctlcluster {} {} stop'.format(self.version, self.name))

    def start(self):
        execute_sync('pg_ctlcluster {} {} start'.format(self.version, self.name))

    def remove_db_directory(self):
        execute_sync('rm -rf {}'.format(self.db_location))

    def setup_wal_receive_service(self):
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
                  f' -v --checkpoint=fast'
        execute_sync(command, env=[('PGPASSWORD', self.master.password)])

        print('change owner to postgres')
        chown(self.db_location, 'postgres')

    def configure_recovery_file(self):
        template_path = Path(__file__).parent / "../templates/{}-recovery.conf".format(self.version)
        template = Template(read_file(template_path))

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
        )

        file_location = f'/etc/postgresql/{self.version}/{self.name}/postgresql.conf' if self.version >= 12 \
            else f'{self.db_location}/recovery.conf'

        write_file(file_location, recovery_config)
        chown(file_location, 'postgres')
