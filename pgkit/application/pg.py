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
    print(name, host, port, version, dbname, username, password, slot, replica_port, shell_to_replica)
    master = Master(name, host, port, version, dbname, username, password, slot)
    replica = Replica(master, replica_port, None)

    if shell_to_replica:
        replica.shell()
    else:
        master.shell()
