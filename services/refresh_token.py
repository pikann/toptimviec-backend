from models.RefreshToken import RefreshToken
from services import db


def create_refresh_token(id, role):
    refreshToken = RefreshToken(id, role)
    db.refresh_token.insert_one(refreshToken.__dict__)
    return refreshToken
