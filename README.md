# pgkit
Postgresql KIT (Backup and PITR)

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

