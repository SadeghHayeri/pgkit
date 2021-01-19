from pgkit.application.utils import execute_sync
from pgkit.application.models import Postgres


class Master(Postgres):
    def __init__(self, name, host, port, version, dbname, username, password, slot):
        super().__init__(name, host, port, version, dbname, username, password, slot)

    def create_replica(self):
        execute_sync('pg_createcluster {} {}'.format(self.version, self.name))

    def remove_replica_directory(self):
        execute_sync('rm -rf {}'.format(self.replica_db_location))

    def start_replica(self):
        execute_sync('pg_ctlcluster {} {} start'.format(self.version, self.name))

    def stop_replica(self):
        execute_sync('pg_ctlcluster {} {} stop'.format(self.version, self.name))
