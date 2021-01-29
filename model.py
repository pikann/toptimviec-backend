from bson.objectid import ObjectId
import datetime

class Post:
    def __init__(self, dict=None):
        if dict is None:
            self._id = ObjectId()
            self.title = ""
            self.content = ""
            self.employer = ObjectId()
            self.place = []
            self.email = ""
            self.phone = ""
            self.salary = ""
            self.deadline = datetime.datetime.now()
        else:
            self._id = dict["_id"]
            self.title = dict["title"]
            self.content = dict["content"]
            self.employer = dict["employer"]
            self.place = dict["place"]
            self.email = dict["email"]
            self.phone = dict["phone"]
            self.salary = dict["salary"]
            self.deadline = dict["deadline"]


class Employer:
    def __init__(self, dict=None):
        if dict is None:
            self._id = ObjectId()
            self.name = ""
            self.bio = ""
            self.avatar = ""
        else:
            self._id = dict["_id"]
            self.name = dict["name"]
            self.bio = dict["bio"]
            self.avatar = dict["avatar"]
