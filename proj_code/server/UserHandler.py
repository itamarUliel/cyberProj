import bcrypt
from proj_code.common.colors import *

class UserHandler:
    @staticmethod
    def set_known_users():
        known_users = {}
        f = open("users.txt", 'r')
        for line in f:
            us, ps = line.split("|")
            known_users[us] = ps.replace("\n", "")
        f.close()
        return known_users

    def __init__(self):
        self.__known_users = self.set_known_users()
        self.__connected_users = []

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

"""
    if not self.get_is_primary():
        backup = self.get_backup_data()
        if data[0] in backup.keys():
            current_conn_data.set_authorize(backup[data[0]])
            print(DATA_COLOR + f"{data[0]} has aa backup, backup load: {backup[data[0]]}")
        else:
            print(DATA_COLOR + f"{data[0]} didn't have backup to load")
"""