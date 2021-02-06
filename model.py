import base64
import os

from bson.objectid import ObjectId
import datetime
from controller import db


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

    def setID(self, i):
        self._id=i


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

    def setID(self, i):
        self._id=i


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


class User:
    def __init__(self, dict=None):
        if dict is None:
            self._id = ObjectId()
            self.email = ""
            self.password = ""
            self.role = ""
            self.validate = ""
        else:
            self._id = dict["_id"]
            self.email = dict["email"]
            self.password = dict["password"]
            self.role = dict["role"]
            self.validate = dict["validate"]

    def id(self):
        return self._id


class Token():
    def __init__(self, id_user):
        self._id = ""
        self.token_expiration = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        self.id_user = id_user

    def get_token(self, expires_in=3600):
        now = datetime.datetime.utcnow()
        if self._id and self.token_expiration > now + datetime.timedelta(seconds=60):
            return self
        self._id = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + datetime.timedelta(seconds=expires_in)
        db.session.insert_one(self.__dict__)
        return self

    def revoke_token(self):
        self.token_expiration = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        e = db.session.update_one({"_id": self._id}, {"$set": {"token_expiration": self.token_expiration}})
        if e.matched_count > 0:
            return "ok"
        else:
            return "error"

    @staticmethod
    def check_token(id_token):
        data = db.session.find_one({"_id": id_token})
        if data is None or data["token_expiration"] < datetime.datetime.utcnow():
            return None
        token = Token(data["id_user"])
        token._id = data["_id"]
        token.token_expiration = data["token_expiration"]
        return token

    def show_token(self):
        return self._id