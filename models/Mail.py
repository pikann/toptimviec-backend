from bson.objectid import ObjectId


class Mail:
    def __init__(self, sender, receiver, title="", content="", attach_post=None, attach_cv=None):
        self._id = ObjectId()
        self.title = title
        self.content = content
        self.sender = sender
        self.receiver = receiver
        self.attach_post = attach_post
        self.attach_cv = attach_cv

    def id(self):
        return self._id