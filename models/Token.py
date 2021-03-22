import datetime


class Token():
    def __init__(self, id_user, role, refresh, token_expiration=None):
        if token_expiration is None:
            self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        else:
            self.token_expiration = token_expiration
        self.id_user = id_user
        self.role = role
        self.refreshToken = refresh