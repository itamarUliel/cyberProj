import select
from threading import Thread
import argparse

from proj_code.server import *
from proj_code.server.ServerConnectionHandler import ServerConnectionHandler
from proj_code.server.BackupConnectionHandler import BackupConnectionHandler
from proj_code.common import *
from proj_code.common import ChatProtocol

ENCRYPT_CONNECTION_STATUS = "encrypt"
PENDING_CONNECTION_STATUS = "pending"
COMM_CONNECTION_STATUS = "comm"


def main(ip=DEFAULT_IP, port=0):
    server = ChatServer((ip, port))
    server.start_running()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str)
    parser.add_argument('--port', type=int)
    args = parser.parse_args()

    if args.ip is not None:
        if args.port is not None:
            main(args.ip, args.port)
        else:
            main(args.ip)
    else:
        main()

