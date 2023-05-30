class HasNoBackupException(BaseException):
    def __init__(self):
        self.message = "there is no backup to connect"

    def __str__(self):
        return f"HasNoBackupException: {self.message}"
