class ConnectionData:
    def __init__(self):
        self.__status = "encrypt"
        self.__user = None
        self.__authorize = []
        self.__public_key = None
        self.__write_socket = None
        self.__write_socket_key = None

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def get_user(self):
        return self.__user

    def set_user(self, user):
        self.__user = user

    def get_authorize(self):
        return self.__authorize

    def set_authorize(self, authorize):
        self.__authorize = authorize

    def update_authorize(self, value):
        self.__authorize.append(value)

    def get_public_key(self):
        return self.__public_key

    def set_public_key(self, public_key):
        self.__public_key = public_key

    def get_write_socket(self):
        return self.__write_socket

    def set_write_socket(self, write_socket):
        self.__write_socket = write_socket

    def get_write_socket_key(self):
        return self.__write_socket_key

    def set_write_socket_key(self, write_socket_key):
        self.__write_socket_key = write_socket_key

