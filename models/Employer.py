from bson.objectid import ObjectId
from services.global_data import list_hashtag


class Employer:
    def __init__(self):
        self._id = ObjectId()
        self.name = ""
        self.bio = ""
        self.avatar = "https://res.cloudinary.com/pikann22/image/upload/v1615044354/toptimviec/TCM27Jw1N8ESc1V0Z3gfriuG1NjS_hXXIww7st_jZ0bFz3xGRjKht7JXzfLoU_ZelO4KPiYFPi-ZBVZcR8wdQXYHnwL5SDFYu1Yf7UBT4jhd9d8gj0lCFBA5VbeVp9SveFfJVKRcLON-OyFX_kxrs3f.png"
        self.hashtag = {h: 0 for h in list_hashtag}

    def id(self):
        return self._id

    def setID(self, i):
        self._id=i