from bson.objectid import ObjectId
import datetime
import jwt
from models.Token import Token
from services import db

SECRET_KEY=b'h\xc9k\xda1\xb9\xc1\xee\xa0\x0cA\xbb\xeb\xb6\x81v\\\xee\xd0\xdc<FT\x18'


def encode(token):
    try:
        payload = {
            'exp': token.token_expiration,
            'sub': {"id_user": str(token.id_user), "role": token.role},
            'iss': str(token.refreshToken)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except:
        return None


def decode(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    except:
        return None

    token_obj = Token(ObjectId(payload['sub']["id_user"]), payload['sub']["role"], ObjectId(payload['iss']),
                      datetime.datetime.fromtimestamp(payload['exp']))
    return token_obj


def revoke_token(token):
    token_expiration = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    e = db.refresh_token.update_one({"_id": token.refreshToken}, {"$set": {"token_expiration": token_expiration}})
    if e.matched_count > 0:
        return "ok"
    else:
        return "error"


def check_token(key):
    token = decode(key)
    if token is None or token.token_expiration < datetime.datetime.utcnow():
        return None
    return token
