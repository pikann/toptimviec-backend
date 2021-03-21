from bson.objectid import ObjectId
import datetime
import jwt
from routes import db

SECRET_KEY=b'h\xc9k\xda1\xb9\xc1\xee\xa0\x0cA\xbb\xeb\xb6\x81v\\\xee\xd0\xdc<FT\x18'


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