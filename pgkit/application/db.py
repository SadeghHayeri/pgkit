from tinydb import TinyDB, Query
from pgkit.application.settings import DB_PATH


class DBClass:
    def __init__(self, db_path):
        self.db = TinyDB(db_path, create_dirs=True)
        self.config_table = self.db.table('config')

    def add_config(self, name, version, host, port, dbname, slot, username, password, replica_port):
        self.config_table.insert({
            'name': name,
            'version': version,
            'host': host,
            'port': port,
            'dbname': dbname,
            'slot': slot,
            'username': username,
            'password': password,
            'replica_port': replica_port
        })

    def remove_config(self, name):
        self.config_table.remove(Query().name == name)

    def get_config(self, name):
        return self.config_table.search(Query().name == name)[0]


DB = DBClass(DB_PATH)
