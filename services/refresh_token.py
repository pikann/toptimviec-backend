from models.RefreshToken import RefreshToken
from services import db


def create_refresh_token(id, role):
    refreshToken = RefreshToken(id, role)
    db.refresh_token.insert_one(refreshToken.__dict__)
    return refreshToken


def get_refresh_token(id_token, key):
    return db.refresh_token.find_one({"_id": id_token, "key": key})
