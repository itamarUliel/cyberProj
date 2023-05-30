import bcrypt
from proj_code.common.colors import *


class UserHandler:
    def __init__(self):
        self.__known_users = self.set_known_users()
        self.__connected_users = []

    @staticmethod
    def set_known_users():
        known_users = {}
        f = open("users.txt", 'r')
        for line in f:
            us, ps = line.split("|")
            known_users[us] = ps.replace("\n", "")
        f.close()
        return known_users

    def login(self, username, pwd):
        try:
            if bcrypt.checkpw(pwd.encode(), self.__known_users[username].encode()):  # 0: us 1: pwd
                if username not in self.__connected_users:
                    print(OK_COLOR + f"{username} is now logged in!")
                    self.__connected_users.append(username)
                    return [True, f"{username} is now logged in!"]

                else:
                    return [False, "user already connected, try again"]

            else:
                return [False, "username or pwd incorrect"]
        except KeyError:
            return [False, "username or pwd incorrect"]

    def close_user(self, user):
        try:
            self.__connected_users.remove(user)
        except ValueError:
            pass
