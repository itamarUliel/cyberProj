import Encryption_handeler

import colorama
from colorama import Back, Fore
colorama.init(autoreset=True)

error_c = Fore.BLACK + Back.RED
ok_c = Back.GREEN + Fore.BLACK
pending_c = Back.LIGHTBLUE_EX + Fore.BLACK
data_c = Back.LIGHTYELLOW_EX + Fore.GREEN

BYTE_SIZE = 1024


def build_login():
    data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
    if data[0] == "exit":
        return None
    try:
        us, ps = data[0], data[1]
        return f"login|{us}|{ps}"
    except IndexError:
        print("try doing better...")
        return build_login()


def connected(s, spb, pr):
    s.sendall(Encryption_handeler.encrypt("connected|", spb))
    data = Encryption_handeler.decrypt(s.recv(BYTE_SIZE), pr)
    conn, auth = data.split("|")
    print(f"""\n
        connected users:\t {"    ".join(conn.split(","))}
        authorize for you:\t {"    ".join(auth.split(","))}
    """)


def build_authorize(s, spb, pr):
    connected(s, spb, pr)
    us2get = input(pending_c + "who you want to get authorize? : ")
    return f"authorize|{us2get}"


def build_sendto_msg(s, spb, pr):
    connected(s, spb, pr)
    us2send = input(pending_c + "who you want to send msg (authorized only)? : ")
    msg = input(pending_c + "what do you want to send?")
    return f"sendto_msg|{us2send}|{msg}"


def build_close():
    return "close|"
