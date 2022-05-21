# PgKit
Postgresql KIT - Backup, PITR and recovery managment made easy

<p align="center">
    <img src="assets/header-blue.png" alt="pgkit logo" width="100%">
</p>
<p align="center">
    <img src="https://img.shields.io/github/license/SadeghHayeri/pgkit.svg?color=green&style=for-the-badge"> <img src="https://img.shields.io/github/repo-size/SadeghHayeri/pgkit.svg?color=green&style=for-the-badge">
</p>

PgKit is an open-source administration tool for disaster recovery of PostgreSQL servers, It allows your organisation to perform remote backups of multiple servers in business critical environments to reduce risk and help DBAs during the recovery phase.

### demo
<a href="https://asciinema.org/a/496249?speed=3&theme=tango&autoplay=1" target="_blank"><img src="https://asciinema.org/a/496249.svg" /></a>

---
## Installation
[pgkit](https://pypi.org/project/pgkit/) can be installed through pip.

As the package works with postgresql, it should be installed as root to have enough privileges.
```shell
$ sudo pip3 install pgkit
```

---
## Usage

pgkit provides a cli with these commands available:
- config
- list
- pitr
- dump
- dumpall
- shell
- start
- stop
- restart

### Config
The `config` command is used to add, get or remove database configs to the kit.<br>
The following sub-commands are available:
- add
- get
- remove

New database configs can be added both using flags or an interactive command prompt.

#### Adding a database config using the flags:
```shell
$ sudo pgkit config add \
  --name <name> \
  --version <version> \
  --host <host-address> \
  --port <host-port> \
  --dbname postgres \
  --slot <slot-name> \
  --username <host-username> \
  --password <host-password> \
  --replica-port <replica-port> \
  --use-separate-wal-receive-service
```

The `replica-port` and `use-separate-wal-receive-service` flags are optional.<br>
The `replica-port` specifies the port on which the replica listens.<br>
The `use-separate-wal-receive-service` flag specifies if pgkit should use a separate service to receive the WAL files
from the host or to let the postgres cluster handle receiving the WAL files itself.

> **Important:** It's best to use a separate receivewal service (set the flag) if setting up a delayed replica (PITR). If setting
> up a real-time replica (zero delay) it is better to let PostgreSQL receive the WAL files itself.

#### Adding a database config using the interactive prompt:
```shell
$ sudo pgkit config add

Name: main
Version (9.5, 10, 11, 12, 13): 12
Host: master
Port: 5432
Dbname: test
Slot: test
Username: test
Password: test
```

#### Getting a config
The `get` command displays an existing config:
```shell
$ sudo pgkit config get <name>

dbname: postgres
host: <host>
max_connections: 100
max_worker_processes: 8
name: <name>
password: <password>
port: <host-port>
replica_port: <replica-port>
slot: <slot>
use_separate_receivewal_service: true|false
username: <host-username>
version: <host-version>

```

#### Removing a config
The `remove` command removes an existing config entry. Using this command requires providing the `--dangerous` flag.
```shell
$ sudo pgkit config remove <name>
```

### List
The list command lists all existing database config entries.
```shell
$ sudo pgkit list

- sample
- testdb
- test2
```

### PITR
The `pitr` command is used to set up backup replicas and recover them.<br>
The following subcommands are available:
- backup
- recover
- promote

#### Backup
This command is used to set up a replica with the desired amount of delay. The delay is in minutes.
```shell
$ sudo pgkit pitr backup <name> <delay>
```

> **Important:** This command may take a while to finish as it starts a base backup which copies the whole data directory
> of the host database. It is best to execute this command in a detachable environment such as `screen` or `tmux`.

#### Recover
This command is used to recover a delayed replica to a specified point in time between now and the database's delay
amount. The time can be given in the `YYYY-mm-ddTHH:MM` format. The `latest` keyword can also be used to recover the
database up to the latest transaction available.
```shell 
$ sudo pgkit pitr recover <name> <time>
$ sudo pgkit pitr recover <name> latest
```

The database will then start replaying the WAL files. It's progress can be tracked through the log files at 
`/var/log/postgresql/`.

#### Promote
This command promotes the replica, separating it from the master database and making it a master.
```shell
$ sudo pgkit pitr promote <name>
```

### Dump
This command is used to create a dump from a single database in a cluster.
```shell
$ sudo pgkit dump <cluster-name> <database-name> <output-path>
```
The command does not compress the dump by default. If the `--compress` flag is given,
then the dump will be compressed. The `--compression-level` flag can also be given along with an argument that
specifies the compression level (1-9). If the compress flag is given without specifying the compression level, 
the default gzip compression level (6) is used.
```shell
$ sudo pgkit dump <cluster-name> <database-name> <output-path> --compress --compression-level 9
```
> The `<cluster-name>` specified in the command above is the name given when adding the database config.

### Dumpall
This command is used to dump the whole cluster into an sql file.
```shell
$ sudo pgkit dumpall <cluster-name> <output-path>
```
The `--compress` and `--compression-level` flags are also available and work as explained above.

### Shell
This command is used to enter the postgresql shell (psql).
```shell
$ sudo pgkit shell <name>
```
If no flags are given, the shell will be connected to the source database. If a shell from the replica database is 
needed, the `--replica` flag must be given.
```shell
$ sudo pgkit shell <name> --replica
```

### Start
This command starts the replica PostgreSQL cluster.
```shell
$ sudo pgkit start <name>
```

### Stop
This command stops the replica PostgreSQL cluster.
```shell
$ sudo pgkit stop <name>
```

### Restart
This command restarts the replica PostgreSQL cluster.
```shell
$ sudo pgkit restarts <name>
```
---
## To-Do
- [ ] Add `replica-port` and `use-separate-wal-receive-service` options to the interactive prompt.
- [ ] Fix the tests.
- [ ] Add `edit` command to the `config` part.
- [ ] Add `status` command to pgkit to show stats about the databases.

## Test Environment
We have created a test environment using docker-compose consisting of one `master` and one `replica` postgresql servers.
To use this environment run:

```bash
cd deployment && sudo docker-compose build && sudo docker-compose up -d
```

Now exec into replica and run:

```bash
pgkit --help
```

### Standby Replication

#### Replication Setup

* Add pgkit config:

```bash
pgkit config add
```

In the `Host` field enter `master`. A tested sample config is given below:

```
Name: main
Version (9.5, 10, 11, 12, 13): 12
Host: master
Port: 5432
Dbname: test
Slot: test
Username: test
Password: test
```

* Start replication process:

```bash
pgkit pitr backup <name> 0
```

#### Restoration Process

* Stop master:

```bash
sudo docker stop master
```

* Exec into replica and recover to latest:

```bash
sudo docker-compose exec replica bash
pgkit pitr recover <name> latest
```

* Promote the replica:

```bash
pgkit pitr promote <name>
```

Now you can test the replica:
* Connect to database `test` and select data:

```bash
su postgres
psql -d test -c "select * from persons"
```

