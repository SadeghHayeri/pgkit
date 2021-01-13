from pgkit.application.utils import execute_sync


class Postgres:
    def __init__(self, name, host, port, version, username, password, slot):
        self.name = name
        self.host = host
        self.port = port
        self.version = version
        self.username = username
        self.password = password
        self.slot = slot

    def run_cmd(self, cmd):
        execute_sync(f'psql -h {self.host} -p {self.port} -U {self.username} {cmd}',
                     env=[('PGPASSWORD', self.password)])

    def force_switch_wal(self):
        command = 'select * from pg_switch_xlog()' if self.version < 10 else 'select * from pg_switch_wal()'
        execute_sync(command)
