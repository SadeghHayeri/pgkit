from pgkit.application.models import Master, Replica


def backup(name, host, port, version, dbname, username, password, slot, replica_port, replica_delay):
    master = Master(name, host, port, version, dbname, username, password, slot)
    replica = Replica(master, replica_port, replica_delay)

    replica.start_backup()


def print_status(name, host, port, version, dbname, username, password, slot, replica_port):
    master = Master(name, host, port, version, dbname, username, password, slot)
    replica = Replica(master, replica_port, None)

    replica.print_status()


def shell(name, host, port, version, dbname, username, password, slot, replica_port, shell_to_replica):
    master = Master(name, host, port, version, dbname, username, password, slot)
    replica = Replica(master, replica_port, None)

    if shell_to_replica:
        replica.shell()
    else:
        master.shell()


def recovery(name, host, port, version, dbname, username, password, slot, replica_port, time_to_recover):
    master = Master(name, host, port, version, dbname, username, password, slot)
    replica = Replica(master, replica_port, None)

    replica.recovery(time_to_recover)


def dump(name, host, port, version, dbname, username, password, slot, replica_port, output_path, compress=False,
         compression_level=9):
    master = Master(name, host, port, version, dbname, username, password, slot)
    replica = Replica(master, replica_port, None)

    replica.dump(output_path, compress, compression_level)
