from tinydb import TinyDB, Query
from pgkit.application.settings import DB_PATH
import os

class DBClass():
    def __init__(self, db_path):
        self.db = TinyDB(db_path)
        self.config_table = self.db.table('config')

    def add_config(self, name, version, host, port, slot, username, password):
        self.config_table.insert({
            'name': name,
            'version': version,
            'host': host,
            'port': port,
            'slot': slot,
            'username': username,
            'password': password,
        })

    def remove_config(self, name):
        self.config_table.remove(Query().name == name)

    def get_config(self, name):
        return self.config_table.search(Query().name == name)[0]

DB = DBClass(DB_PATH)
