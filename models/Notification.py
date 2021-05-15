import datetime
from bson.objectid import ObjectId


class Notification:
    def __init__(self, user, type, id_attach, content, img):
        self._id = ObjectId()
        self.user = user
        self.type = type
        self.id_attach = id_attach
        self.content = content
        self.img = img
        self.read = False
        self.time = datetime.datetime.utcnow()
    def id(self):
        return self._id