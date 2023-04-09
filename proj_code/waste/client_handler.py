import Encryption_handler
import sys

from colors import *

from proj_code.waste.client_utils import BYTE_SIZE


def build_login(bm, user_backup):
    if not bm or (bm and user_backup is None):
        try:
            data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
        except ValueError:
            sys.stdin = open(0, 'r')
            data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
        if data[0] == "exit":
            return None
        try:
            us, ps = data[0], data[1]
            return f"login|{us}|{ps}"
        except IndexError:
            print("try doing better...")
            return build_login(bm, user_backup)
    else:
        return f"login|{user_backup[0]}|{user_backup[1]}"


def connected(s, spb, pr):
    s.sendall(Encryption_handler.encrypt("connected|", spb))
    data = Encryption_handler.decrypt(s.recv(BYTE_SIZE), pr)
    conn, auth = data.split("|")
    print(f"""\n
        connected users:\t {"    ".join(conn.split(","))}
        authorize for you:\t {"    ".join(auth.split(","))}
    """)


def build_authorize(s, spb, pr):
    connected(s, spb, pr)
    us2get = input(PENDING_COLOR + "who you want to get authorize? : ")
    return f"authorize|{us2get}"


def build_sendto_msg(s, spb, pr):
    connected(s, spb, pr)
    us2send = input(PENDING_COLOR + "who you want to send msg (authorized only)? : ")
    msg = input(PENDING_COLOR + "what do you want to send?")
    return f"sendto_msg|{us2send}|{msg}"


def build_close():
    return "close|"


class NeedBackupException(Exception):
    def __init__(self, message="the main server falled. need to move backup"):
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"
