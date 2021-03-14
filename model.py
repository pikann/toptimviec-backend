import base64
import os

from bson.objectid import ObjectId
import datetime
import jwt
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
            self.hashtag = {h: 0 for h in list_hashtag}
        else:
            self._id = dict["_id"]
            self.name = dict["name"]
            self.bio = dict["bio"]
            self.avatar = dict["avatar"]
            self.url = dict["url"]
            self.hashtag = dict["hashtag"]

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
    def __init__(self, dict=None, applicant=None):
        if dict is None:
            self._id = ObjectId()
            self.name = ""
            self.gender = True
            self.avatar = ""
            self.position = ""
            self.dob = datetime.datetime.now()
            self.address = ""
            self.email = ""
            self.phone = ""
            self.place = ""
            self.skill = []
            self.hashtag = []
            self.content = []
            self.interests = []
            self.find_job = True
            if applicant is None:
                self.applicant = ObjectId()
            else:
                self.applicant = applicant
        else:
            self._id = dict["_id"]
            self.name = dict["name"]
            self.gender = dict["gender"]
            self.avatar = dict["avatar"]
            self.position = dict["position"]
            self.dob = dict["dob"]
            self.address = dict["address"]
            self.email = dict["email"]
            self.phone = dict["phone"]
            self.place = dict["place"]
            self.skill = dict["skill"]
            self.hashtag = dict["hashtag"]
            self.content = dict["content"]
            self.interests = dict["interests"]
            self.find_job = dict["find_job"]
            self.applicant = dict["applicant"]

    def id(self):
        return self._id

    @staticmethod
    def check_skill(skills):
        for skill in skills:
            if skill.__class__ != dict:
                return False
            if not "skill" in skill or not "rate" in skill or len(skill)!=2:
                return False
            if skill["skill"].__class__!=str or skill["rate"].__class__!=int:
                return False
            if skill["rate"]>5 or skill["rate"]<1:
                return False
        return True

    @staticmethod
    def check_content(contents):
        for content in contents:
            if content.__class__ != dict:
                return False
            if not "title" in content or not "content" in content or len(content) != 2:
                return False
            if content["title"].__class__!=str or content["content"].__class__!=list:
                return False
            if not CV_Block.check_content(content["content"]):
                return False
        return True


class CV_Block:
    def __init__(self):
        self.title=""
        self.content=[]

    @staticmethod
    def check_content(contents):
        for content in contents:
            if content.__class__ != dict:
                return False
            if not "title" in content or not "position" in content or not "time" in content or not "detail" in content or len(content) != 4:
                return False
            if content["title"].__class__!=str or content["position"].__class__!=str or content["time"].__class__!=str or content["detail"].__class__!=str:
                return False
        return True


class CV_Row:
    def __init__(self):
        self.title=""
        self.position=""
        self.time=datetime.datetime.now()
        self.detail=""


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
    def __init__(self, id_user, role, refresh, token_expiration=None):
        if token_expiration is None:
            self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        else:
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
            payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        except:
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
    def __init__(self, sender, receiver, title="", content="", attach_post=None, attach_cv=None):
        self._id = ObjectId()
        self.title = title
        self.content = content
        self.sender = sender
        self.receiver = receiver
        self.attach_post = attach_post
        self.attach_cv = attach_cv



class List_Candidate:
    def __init__(self, employer):
        self._id = ObjectId()
        self.name = ""
        self.employer = employer
        self.list = []

    def id(self):
        return self._id
