from proj_code.server import *
from proj_code.common import *


def main():
    prime = ChatServer(True, PRIMARY_ADDRESS)
    prime.start_running()


if __name__ == '__main__':
    main()
