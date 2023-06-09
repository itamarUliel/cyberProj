from proj_code.client import *
from threading import Thread


class ChatClient:

    def __init__(self):
        self.__user_backup = None
        self.__conn_handler = ClientConnectionHandler()
        self.__listener = None

    def start_listener(self):
        self.__listener = Thread(target=ChatClientListener.do_listen, args=[self.__conn_handler]).start()

    def close_connection(self):
        self.__conn_handler.close_connection()
        exit()

    def authorize(self):
        self.get_connected_users()
        username = input("who you want to get authorize? :...")
        self.__conn_handler.authorize(username)

    def allow(self):
        self.see_waiting()
        username_to_allow = input("who you want to allow? :...")
        self.__conn_handler.allow(username_to_allow)

    def send_message(self):
        self.get_connected_users()
        target_user = input("who do you want to send:")
        msg = None
        print(f"enter send mode, user: {target_user}\nto exit enter 'exit_sending'")
        while True:
            msg = input("...:")
            if msg == 'exit_sending':
                break
            chk = self.__conn_handler.send_message(target_user, msg)
            if not chk:
                break

    def see_waiting(self):
        waiting = self.__conn_handler.see_waiting()
        if waiting is not None:
            print(f"""\n
            waiting to allow:\t {"    ".join(waiting)}
            """)

    def get_connected_users(self):
        try:
            conn, auth = self.__conn_handler.get_connected_users()
            print(f"""\n
            connected users:\t {"    ".join(conn.split(","))}
            authorize for you:\t {"    ".join(auth.split(","))}
            """)
        except AttributeError:
            raise ConnectionError

    def login(self):
        valid_user = False
        while not valid_user:
            if self.__user_backup is None:
                try:
                    data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
                except ValueError:
                    sys.stdin = open(0, 'r')
                    data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
                if data[0] == "exit":
                    self.close_connection()
            else:
                data = self.__user_backup

            try:
                username, pwd = data[0], data[1]
                valid_user = self.__conn_handler.login(username, pwd)
                if valid_user:
                    self.__user_backup = (username, pwd)
                else:
                    self.__user_backup = None
            except IndexError:
                valid_user = False

            if not valid_user:
                print("try doing better...")

    def start_encrypt(self):
        self.__conn_handler.start_encrypt()

    def restart_conn_handler(self):
        self.__conn_handler.close_all_sockets()
        self.__conn_handler = ClientConnectionHandler()

    def run(self):
        self.start_encrypt()
        self.login()
        self.start_listener()

        while True:
            show = """\n
                        'a' = ask server to authorize this user
                        'm' = write a message
                        'e' = close connection (exit)
                        'c' = see who's connected and who you can talk to
                        'w' = see who's waiting to get authorize by you
                        'A' = allow someone to send you message
                        """
            print(show)
            try:
                act = input("\t\t\tact:")[0]
            except IndexError:
                print("try again...")
                continue

            except ValueError:
                sys.stdin = open(0, 'r')
                act = input("\t\t\tact:")[0]

            if act in ['a', 'm', 'e', 'c', 'w', 'A']:
                if act == 'e':
                    self.close_connection()
                elif act == 'a':
                    self.authorize()
                elif act == 'c':
                    self.get_connected_users()
                elif act == 'm':
                    self.send_message()
                elif act == 'w':
                    self.see_waiting()
                elif act == 'A':
                    self.allow()


def start_client():
    chat_client = ChatClient()
    while True:
        try:
            chat_client.run()
        except ConnectionError:
            chat_client.restart_conn_handler()
            continue

def main():
    start_client()


if __name__ == '__main__':
    main()
