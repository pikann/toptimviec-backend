import random
import string
from bson.objectid import ObjectId
import datetime


class RefreshToken:
    def __init__(self, id_user, role):
        self._id = ObjectId()
        self.key = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(60))
        self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        self.id_user = id_user
        self.role = role

    def show_key(self):
        return str(self._id)+"."+self.key

    def id(self):
        return self._id