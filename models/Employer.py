from bson.objectid import ObjectId
from services.global_data import list_hashtag


class Employer:
    def __init__(self):
        self._id = ObjectId()
        self.name = ""
        self.bio = ""
        self.avatar = ""
        self.url = ""
        self.hashtag = {h: 0 for h in list_hashtag}

    def id(self):
        return self._id

    def setID(self, i):
        self._id=i