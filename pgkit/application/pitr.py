from pgkit.models.master import Master
from pgkit.models.replica import Replica


def backup(name, host, port, version, username, password, slot, replica_port, replica_delay):
    master = Master(name, host, port, version, username, password, slot)
    replica = Replica(master, replica_port, replica_delay)

    replica.start_backup()
