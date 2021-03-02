import base64
import os

from bson.objectid import ObjectId
import datetime
import jwt
from jwt.exceptions import ExpiredSignatureError
from controller import db, list_hashtag

SECRET_KEY=b'h\xc9k\xda1\xb9\xc1\xee\xa0\x0cA\xbb\xeb\xb6\x81v\\\xee\xd0\xdc<FT\x18'


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
            self.hashtag = {h: 0 for h in list_hashtag}
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
            self.hashtag = dict["hashtag"]

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
    def __init__(self, id_user, role, refresh, token_expiration=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)):
        self.token_expiration = token_expiration
        self.id_user = id_user
        self.role = role
        self.refreshToken = refresh

    def encode(self):
        try:
            payload = {
                'exp': self.token_expiration,
                'sub': {"id_user": str(self.id_user), "role": self.role},
                'iss': str(self.refreshToken)
            }
            return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        except:
            return None

    @staticmethod
    def decode(token):
        try:
            payload = jwt.decode(token, SECRET_KEY)
        except ExpiredSignatureError:
            return None
        token_obj=Token(ObjectId(payload['sub']["id_user"]), payload['sub']["role"], ObjectId(payload['iss']), datetime.datetime.fromtimestamp(payload['exp']))
        return token_obj

    def revoke_token(self):
        token_expiration = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        e = db.refresh_token.update_one({"_id": self.refreshToken}, {"$set": {"token_expiration": token_expiration}})
        if e.matched_count > 0:
            return "ok"
        else:
            return "error"

    @staticmethod
    def check_token(key):
        token = Token.decode(key)
        if token is None or token.token_expiration < datetime.datetime.utcnow():
            return None
        return token


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


class Mail:
    def __init__(self, sender, receiver, title="", content=""):
        self._id = ObjectId()
        self.title = title
        self.content = content
        self.sender = sender
        self.receiver = receiver
