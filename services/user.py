from services import db
import hashlib


def check_email(email):
    return db.user.find_one({"email": email}) is None


def check_password(email, password):
    return db.user.find_one({"email": email, "password": hashlib.md5(password.encode('utf-8')).hexdigest()})