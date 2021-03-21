from bson.objectid import ObjectId


class List_Candidate:
    def __init__(self, employer):
        self._id = ObjectId()
        self.name = ""
        self.employer = employer
        self.list = []

    def id(self):
        return self._id