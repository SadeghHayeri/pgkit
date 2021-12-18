import subprocess

from pgkit.application.settings import DB_PATH


EXPECTED_CONFIG = '{"config": {"1": {"name": "test", "version": "12", "host": "172.26.0.2", "port": 5432, "dbname": "test", "slot": "replica-test", "username": "testuser", "password": "test-pass", "replica_port": "5432", "max_connections": 100, "max_worker_processes": 8}}}'


def check_config(actual_config):
    assert actual_config == EXPECTED_CONFIG, f"{actual_config} is not equal to expected config {EXPECTED_CONFIG}"
    print("Config is good")


def test_add_config():
    subprocess.run(
        [
            "bash",
            "-c",
            "pgkit config add --name test --version 12 --host 172.26.0.2 --port 5432 --dbname test --slot replica-test --username testuser --password test-pass --replica-port 5432"
        ],
        capture_output=False
    )

    with open(DB_PATH, 'r') as f:
        lines = f.readlines()
        check_config(lines[0])


def test_get_config():
    output = subprocess.check_output("pgkit config get test", shell=True)
    output = output.decode('utf-8').strip().split('\n')
    assert output[0] == "dbname: test"
    assert output[1] == "host: 172.26.0.2"
    assert output[2] == "max_connections: 100"
    assert output[3] == "max_worker_processes: 8"
    assert output[4] == "name: test"
    assert output[5] == "password: test-pass"
    assert output[6] == "port: 5432"
    assert output[7] == "replica_port: '5432'"
    assert output[8] == "slot: replica-test"
    assert output[9] == "username: testuser"
    assert output[10] == "version: '12'"


test_add_config()
test_get_config()
