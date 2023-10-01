import os
import stat
import subprocess
import pathlib
from time import sleep

from pgkit.application.settings import DB_PATH


EXPECTED_CONFIG = '{"config": {"1": {"name": "main", "version": "12", "host": "master", "port": 5432, "dbname": "test", "slot": "replicaslottest", "username": "testuser", "password": "test-pass", "replica_port": "5432", "use_separate_receivewal_service": false, "max_connections": 100, "max_worker_processes": 8}}}'

pgpass_file = str(pathlib.Path.home()) + '/.pgpass'
with open(pgpass_file, 'w+') as f:
    f.write(f'master:5432:test:testuser:test-pass\n')
    f.write(f'replica:5432:test:testuser:test-pass\n')
    f.write(f'replica:5433:test:testuser:test-pass')
os.chmod(pgpass_file, stat.S_IRUSR | stat.S_IWUSR)


def insert(host, port, dbname, username, id, lastname, firstname, age):
    process = subprocess.Popen(
        f"psql -h {host} -p {port} -d {dbname} -U {username} -c \"insert into persons (ID, LastName, FirstName, Age) values ({id}, '{lastname}', '{firstname}', {age})\"",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    result = process.communicate()

    return tuple(x.decode("utf-8").strip() if x else "" for x in result), process.returncode


def check_failing_insert(host, port, dbname, username, id, lastname, firstname, age):
    result, returncode = insert(host, port, dbname, username, id, lastname, firstname, age)
    assert returncode == 1, f"Non one returncode {returncode}"
    assert result[1] == "ERROR:  cannot execute INSERT in a read-only transaction", f"Output: {result[1]}"


def check_successful_insert(host, port, dbname, username, id, lastname, firstname, age):
    result, returncode = insert(host, port, dbname, username, id, lastname, firstname, age)
    assert returncode == 0, f"Non zero retuncode for promotion {returncode}"
    assert result[0] == "INSERT 0 1", f"Wrong output: {result[0]}"
    assert len(result[1]) == 0, f"Non empty stderr: {result[1]}"


def open_pg_hba(cluster_name):
    subprocess.run(f"echo \"host    all             all             0.0.0.0/0               md5\" >> /etc/postgresql/12/{cluster_name}/pg_hba.conf", shell=True)
    subprocess.run(f"systemctl reload postgresql@12-{cluster_name}.service", shell=True)


def check_config(actual_config):
    assert actual_config == EXPECTED_CONFIG, f"{actual_config} is not equal to expected config {EXPECTED_CONFIG}"
    print("Config is good")


def same_query_on_replica_and_master(replica_host, replica_port, master_host, master_port, dbname, username, query):
    master_output = subprocess.check_output(f"psql -h {master_host} -p {master_port} -d {dbname} -U {username} -c \"{query}\"", shell=True)
    replica_output = subprocess.check_output(f"psql -h {replica_host} -p {replica_port} -d {dbname} -U {username} -c \"{query}\"", shell=True)
    master_output = master_output.decode('utf-8')
    replica_output = replica_output.decode('utf-8')
    print(master_output)
    print(replica_output)

    return master_output, replica_output


def check_same_query_on_replica_and_master_expect_sync(replica_host, replica_port, master_host, master_port, dbname, username, query):
    master_output, replica_output = same_query_on_replica_and_master(replica_host, replica_port, master_host, master_port, dbname, username, query)
    assert master_output == replica_output


def check_same_query_on_replica_and_master_expect_unsync(replica_host, replica_port, master_host, master_port, dbname, username, query):
    master_output, replica_output = same_query_on_replica_and_master(replica_host, replica_port, master_host, master_port, dbname, username, query)
    assert master_output != replica_output


def add_config(cluster_name, master_host, replica_slot, replica_port, use_separate_wal_receive_service=False):
    command = (f"pgkit config add --name {cluster_name} " +
        "--version 12 --host {master_host}" +
        " --port 5432 --dbname test --slot {replica_slot}" +
        " --username testuser --password test-pass" +
        " --replica-port {replica_port}")
    if use_separate_wal_receive_service:
        command += " --use-separate-wal-receive-service"
    subprocess.run(
        command,
        shell=True
    )


def test_add_config():
    add_config("main", "master", "replicaslottest", 5432)

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
    assert output[9] == "use_separate_receivewal_service: false"
    assert output[10] == "username: testuser"
    assert output[11] == "version: '12'"


def test_pitr_0_delay_backup():
    subprocess.run("pgkit pitr backup main 0", shell=True)
    open_pg_hba("main")
    check_same_query_on_replica_and_master_expect_sync('replica', 5432, 'master', 5432, 'test', 'testuser', "select * from persons")
    check_successful_insert('master', 5432, 'test', 'testuser', 2, 'Alice', 'Wonderlander', 17)
    sleep(5)
    subprocess.run("pgkit pitr recover main latest", shell=True)
    check_same_query_on_replica_and_master_expect_sync('replica', 5432, 'master', 5432, 'test', 'testuser', "select * from persons")


def test_promote_backup():
    check_failing_insert('replica', 5432, 'test', 'testuser', 3, 'Eleven', 'Eleven', 15)

    process = subprocess.Popen("pgkit pitr promote main", shell=True)
    result = process.communicate()
    result = tuple(x.decode("utf-8").strip() if x else "" for x in result)
    assert process.returncode == 0, f"Non zero retuncode for promotion {process.returncode}"
    assert len(result[0]) == 0, f"Non empty stdout: {result[0]}"
    assert len(result[1]) == 0, f"Non empty stderr: {result[1]}"

    check_successful_insert('replica', 5432, 'test', 'testuser', 3, 'Eleven', 'Eleven', 15)


def test_pitr_recover():
    add_config("pitr" , "master", "replicapitrslot", 5433, True)

    subprocess.run("pgkit pitr backup pitr 180", shell=True)
    open_pg_hba("pitr")

    check_same_query_on_replica_and_master_expect_sync('replica', 5433, 'master', 5432, 'test', 'testuser', "select * from persons")
    check_successful_insert('master', 5432, 'test', 'testuser', 3, 'Eleven', 'Eleven', 15)
    check_same_query_on_replica_and_master_expect_unsync('replica', 5433, 'master', 5432, 'test', 'testuser', "select * from persons")

    subprocess.run("pgkit pitr recover pitr latest", shell=True)
    sleep(5)
    check_same_query_on_replica_and_master_expect_sync('replica', 5433, 'master', 5432, 'test', 'testuser', "select * from persons")


test_add_config()
test_get_config()
test_pitr_0_delay_backup()
test_promote_backup()
test_pitr_recover()
