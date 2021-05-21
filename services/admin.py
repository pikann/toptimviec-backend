from services import db
import datetime


def count_cv():
    return db.cv.find({}).count()


def count_applicant():
    return db.applicant.find({}).count()


def count_employer():
    return db.employer.find({}).count()


def count_post():
    return db.post.find({}).count()


def count_post_unexpired():
    return db.post.find({"deadline": {"$gte": datetime.datetime.utcnow()}}).count()


def count_user():
    return db.user.find({}).count()
