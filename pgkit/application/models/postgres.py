from pgkit.application.utils import execute_sync, to_number


class Postgres:
    def __init__(self, name, host, port, version, dbname, username, password, slot):
        self.name = name
        self.host = host
        self.port = to_number(port)
        self.version = to_number(version)
        self.dbname = dbname
        self.username = username
        self.password = password
        self.slot = slot

    def run_cmd(self, cmd):
        return execute_sync(f'psql -h {self.host} -p {self.port} -U {self.username} -d {self.dbname} -c "{cmd}"',
                     env=[('PGPASSWORD', self.password)])

    def force_switch_wal(self):
        pg_command = 'select * from pg_switch_xlog()' if self.version < 10 else 'select * from pg_switch_wal()'
        self.run_cmd(pg_command)

    def shell(self):
        execute_sync(f'psql -h {self.host} -p {self.port} -U {self.username} -d {self.dbname}',
                     env=[('PGPASSWORD', self.password)])
