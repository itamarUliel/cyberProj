from ConnectionHandler import ConnectionHandler
from ChatListener import ChatListener
from threading import Thread
import sys

class ChatClient:

    def __init__(self):
        self.conn_handler = ConnectionHandler()
        self.listener = None

    def start_listener(self):
        self.listener = Thread(target=ChatListener.do_listen, args=[self.conn_handler]).start()

    def close_connection(self):
        self.conn_handler.close_connection()
        exit()

    def authorize(self):
        self.get_connected_users()
        username = input("who you want to get authorize? : ")
        self.conn_handler.authorize(username)

    def send_message(self):
        self.get_connected_users()
        target_user = input("who do you want to send:")
        msg = input("what to send?: ")
        self.conn_handler.send_message(target_user, msg)

    def get_connected_users(self):
        conn, auth = self.conn_handler.get_connected_users()
        print(f"""\n
        connected users:\t {"    ".join(conn.split(","))}
        authorize for you:\t {"    ".join(auth.split(","))}
        """)

    def login(self):
        valid_user = False
        while not valid_user:
            try:
                data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
            except ValueError:
                sys.stdin = open(0, 'r')
                data = input("\t\tenter us then password (split with space) (or write 'exit' to exit)").split()
            if data[0] == "exit":
                self.close_connection()
            try:
                username, pwd = data[0], data[1]
                valid_user = self.conn_handler.login(username, pwd)
            except IndexError:
                valid_user = False

            if not valid_user:
                print("try doing better...")

    def start_encrypt(self):
        self.conn_handler.start_encrypt()

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

            if act in ['a', 'm', 'e', 'c']:
                if act == 'e':
                    self.close_connection()
                elif act == 'a':
                    self.authorize()
                elif act == 'c':
                    self.get_connected_users()
                elif act == 'm':
                    self.send_message()


def main():
    chat_client = ChatClient()
    chat_client.run()

if __name__ == '__main__':
    main()
