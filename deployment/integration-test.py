import os
import stat
import subprocess
import pathlib
from time import sleep
from pgkit.application.models import master, replica

from pgkit.application.settings import DB_PATH


EXPECTED_CONFIG = '{"config": {"1": {"name": "main", "version": "12", "host": "master", "port": 5432, "dbname": "test", "slot": "replicaslottest", "username": "testuser", "password": "test-pass", "replica_port": "5432", "max_connections": 100, "max_worker_processes": 8}}}'


def check_config(actual_config):
    assert actual_config == EXPECTED_CONFIG, f"{actual_config} is not equal to expected config {EXPECTED_CONFIG}"
    print("Config is good")


def test_add_config():
    subprocess.run(
        [
            "bash",
            "-c",
            "pgkit config add --name main --version 12 --host master --port 5432 --dbname test --slot replicaslottest --username testuser --password test-pass --replica-port 5432"
        ],
        capture_output=False
    )

    with open(DB_PATH, 'r') as f:
        lines = f.readlines()
        check_config(lines[0])


def test_get_config():
    output = subprocess.check_output("pgkit config get main", shell=True)
    output = output.decode('utf-8').strip().split('\n')
    assert output[0] == "dbname: test"
    assert output[1] == "host: master"
    assert output[2] == "max_connections: 100"
    assert output[3] == "max_worker_processes: 8"
    assert output[4] == "name: main"
    assert output[5] == "password: test-pass"
    assert output[6] == "port: 5432"
    assert output[7] == "replica_port: '5432'"
    assert output[8] == "slot: replicaslottest"
    assert output[9] == "username: testuser"
    assert output[10] == "version: '12'"


def test_pitr_backup():
    pgpass_file = str(pathlib.Path.home()) + '/.pgpass'
    with open(pgpass_file, 'w+') as f:
        f.write(f'master:5432:test:testuser:test-pass\n')
        f.write(f'replica:5432:test:testuser:test-pass')
    os.chmod(pgpass_file, stat.S_IRUSR | stat.S_IWUSR)
    subprocess.run("pgkit pitr backup main 0", shell=True)
    subprocess.run("echo \"host    all             all             0.0.0.0/0               md5\" >> /etc/postgresql/12/main/pg_hba.conf", shell=True)
    subprocess.run("service postgresql reload", shell=True)
    master_output = subprocess.check_output("psql -h master -p 5432 -d test -U testuser -c \"SELECT * FROM persons\"", shell=True)
    replica_output = subprocess.check_output("psql -h replica -p 5432 -d test -U testuser -c \"SELECT * FROM persons\"", shell=True)
    master_output = master_output.decode('utf-8')
    replica_output = replica_output.decode('utf-8')
    print(master_output)
    print(replica_output)
    assert master_output == replica_output


test_add_config()
test_get_config()
test_pitr_backup()
