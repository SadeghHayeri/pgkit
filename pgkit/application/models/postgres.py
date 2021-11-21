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

    def run_cmd(self, cmd, without_headers=False):
        env = [('PGPASSWORD', self.password)] if self.password else []
        return execute_sync(f'psql -h {self.host} -p {self.port} -U {self.username} -d {self.dbname} -c "{cmd}"'
                            f' {"-t" if without_headers else ""}',
                            env=env)

    def force_switch_wal(self):
        pg_command = 'select * from pg_switch_xlog()' if self.version < 10 else 'select * from pg_switch_wal()'
        self.run_cmd(pg_command)

    def shell(self):
        env = [('PGPASSWORD', self.password)] if self.password else []
        execute_sync(f'psql -h {self.host} -p {self.port} -U {self.username} -d postgres',
                     env=env, no_pipe=True)

    def create_replication_slot(self):
        args = {'slot_name': f"'{self.slot}'"}
        if self.version != 9.5:
            args['immediately_reserve'] = 'true'
        pg_command = f'select pg_create_physical_replication_slot({", ".join([f"{k} := {v}" for k, v in args.items()])})'
        self.run_cmd(pg_command)

    def drop_replication_slot(self):
        pg_command = f"select pg_drop_replication_slot('{self.slot}')"
        self.run_cmd(pg_command)

    def get_config_parameter_value(self, parameter):
        pg_command = f'SHOW {parameter};'
        result = self.run_cmd(pg_command, without_headers=True)
        if result:
            return result[0].decode().replace('\n', '').replace('\t', '')
        raise Exception('Cannot get parameter')