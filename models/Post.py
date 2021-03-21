from bson.objectid import ObjectId
import datetime


class Post:
    def __init__(self):
        self._id = ObjectId()
        self.title = ""
        self.description = ""
        self.request = ""
        self.benefit = ""
        self.employer = ObjectId()
        self.place = []
        self.salary = ""
        self.deadline = datetime.datetime.now()
        self.url = ""
        self.hashtag = []
        self.address = ""

    def id(self):
        return self._id