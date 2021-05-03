from bson.objectid import ObjectId


class User:
    def __init__(self):
        self._id = ObjectId()
        self.email = ""
        self.password = ""
        self.role = ""
        self.validate = ""
        self.ban = False

    def id(self):
        return self._id