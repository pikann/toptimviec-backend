from bson.objectid import ObjectId
import datetime


class Post:
    def __init__(self, dict=None):
        if dict is None:
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
        else:
            self._id = dict["_id"]
            self.title = dict["title"]
            self.description = dict["description"]
            self.request = dict["request"]
            self.benefit = dict["benefit"]
            self.employer = dict["employer"]
            self.place = dict["place"]
            self.salary = dict["salary"]
            self.deadline = dict["deadline"]
            self.url = dict["url"]


class Employer:
    def __init__(self, dict=None):
        if dict is None:
            self._id = ObjectId()
            self.name = ""
            self.bio = ""
            self.avatar = ""
            self.url = ""
        else:
            self._id = dict["_id"]
            self.name = dict["name"]
            self.bio = dict["bio"]
            self.avatar = dict["avatar"]
            self.url = dict["url"]