import subprocess

from pgkit.application.settings import DB_PATH


EXPECTED_CONFIG = '{"config": {"1": {"name": "test", "version": "12", "host": "172.26.0.2", "port": 5432, "dbname": "test", "slot": "replica-test", "username": "test", "password": "test", "replica_port": "5432", "max_connections": 100, "max_worker_processes": 8}}}'


def add_config():
    subprocess.run(
        [
            "bash",
            "-c",
            "pgkit config add --name test --version 12 --host 172.26.0.2 --port 5432 --dbname test --slot replica-test --username test --password test --replica-port 5432"
        ],
        capture_output=False
    )

    with open(DB_PATH, 'r') as f:
        lines = f.readlines()
        if lines[0] != EXPECTED_CONFIG:
            print("Config is not ok")
            print(f"Real config {lines[0]}")
            print(f"Expected config {EXPECTED_CONFIG}")
            exit(1)
        else:
            print("Config is good")

add_config()
