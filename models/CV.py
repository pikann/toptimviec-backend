from bson.objectid import ObjectId
import datetime


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