from bson.objectid import ObjectId
from routes import list_hashtag
import datetime


class Applicant:
    def __init__(self):
        self._id = ObjectId()
        self.name = ""
        self.gender = True
        self.avatar = ""
        self.dob = datetime.datetime.now()
        self.place = ""
        self.list_CV = []
        self.main_CV = ObjectId()
        self.url = ""
        self.hashtag = {h: 0 for h in list_hashtag}

    def id(self):
        return self._id

    def setID(self, i):
        self._id=i
