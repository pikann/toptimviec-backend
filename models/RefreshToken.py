import base64
import os

from bson.objectid import ObjectId
import datetime


class RefreshToken:
    def __init__(self, id_user, role):
        self._id = ObjectId()
        self.key = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        self.id_user = id_user
        self.role = role

    def show_key(self):
        return str(self._id)+"."+self.key

    def id(self):
        return self._id