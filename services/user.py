from services import db
import hashlib


def check_email(email):
    return db.user.find_one({"email": email}) is None


def check_password(email, password):
    return db.user.find_one({"email": email, "password": hashlib.md5(password.encode('utf-8')).hexdigest()})


def get_user_by_email(email, attribute=None):
    if attribute is None:
        return db.user.find_one({"email": email})
    return db.user.find_one({"email": email}, attribute)


def get_user_by_id(id_user, attribute):
    return db.user.find_one({"_id": id_user}, attribute)


def get_uset_by_validate_key(id_user, key):
    return db.user.find_one({"_id": id_user, "validate": key})


def update_validate(id_user):
    db.user.update_one({"_id": id_user}, {"$set": {"validate": ""}})


def reset_password(id_user, old_password, new_password):
    rs = db.user.update_one(
        {"_id": id_user, "password": hashlib.md5(old_password.encode('utf-8')).hexdigest()},
        {"$set": {"password": hashlib.md5(new_password.encode('utf-8')).hexdigest()}}
    )
    return rs.matched_count
