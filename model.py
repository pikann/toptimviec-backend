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
            self.hashtag = []
            self.address = ""
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
            self.hashtag = dict["hashtag"]
            self.address = dict["address"]

    def id(self):
        return self._id


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

    def id(self):
        return self._id


class Applicant:
    def __init__(self, dict=None):
        if dict is None:
            self._id = ObjectId()
            self.name = ""
            self.gender = True
            self.avatar = ""
            self.dob = datetime.datetime.now()
            self.place = ""
            self.list_CV = []
            self.main_CV = ObjectId()
            self.url = ""
        else:
            self._id = dict["_id"]
            self.name = dict["name"]
            self.gender = dict["gender"]
            self.avatar = dict["avatar"]
            self.dob = dict["dob"]
            self.place = dict["place"]
            self.list_CV = dict["list_CV"]
            self.main_CV = dict["main_CV"]
            self.url = dict["url"]

    def id(self):
        return self._id


class CV:
    def __init__(self, dict=None):
        if dict is None:
            self._id = ObjectId()
            self.url = ""
            self.hashtag = []
        else:
            self._id = dict["_id"]
            self.url = dict["url"]
            self.hashtag = dict["hashtag"]

    def id(self):
        return self._id