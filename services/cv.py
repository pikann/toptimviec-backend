import math

from services import db
from models.CV import CV


def recommend_cv(id_user, list_showed, place):
    db_request = [{"$match": {"_id": id_user}},
                  {"$project": {"hashtag": {"$objectToArray": "$hashtag"}, "_id": 0}},
                  {"$unwind": "$hashtag"},
                  {"$lookup": {
                      "from": "cv",
                      "localField": "hashtag.k",
                      "foreignField": "hashtag",
                      "as": "cv"
                  }},
                  {"$unwind": "$cv"},
                  {"$group": {
                      "_id": "$cv._id",
                      "name": {"$first": "$cv.name"},
                      "avatar": {"$first": "$cv.avatar"},
                      "position": {"$first": "$cv.position"},
                      "hashtag": {"$first": "$cv.hashtag"},
                      "find_job": {"$first": "$cv.find_job"},
                      "place": {"$first": "$cv.place"},
                      "count_find": {"$sum": "$hashtag.v"}
                  }},
                  {"$match": {"_id": {"$not": {"$in": list_showed}}}},
                  {"$match": {"find_job": True}}]
    if place != "":
        db_request += [{"$match": {"place": place}}]

    db_request += [{"$sort": {"count_find": -1, "_id": -1}},
                   {"$limit": 20},
                   {"$project": {
                       "count_find": 0,
                       "find_job": 0
                   }},
                   {"$set": {
                       "_id": {"$toString": "$_id"}
                   }}]
    return list(db.employer.aggregate(db_request))


def find_list_cv(list_showed, hashtag, place):
    db_request = [{"$match": {"_id": {"$not": {"$in": list_showed}}}},
                  {"$match": {"find_job": True}}]
    if place != "":
        db_request += [{"$match": {"place": place}}]
    db_request += [{"$unwind": "$hashtag"},
                   {"$match": {"hashtag": {"$in": hashtag}}},
                   {"$group": {
                       "_id": "$_id",
                       "name": {"$first": "$name"},
                       "avatar": {"$first": "$avatar"},
                       "position": {"$first": "$position"},
                       "hashtag": {"$first": "$hashtag"},
                       "find_job": {"$first": "$find_job"},
                       "place": {"$first": "$place"},
                       "count_find": {"$sum": 1}
                   }},
                   {"$sort": {"count_find": -1, "_id": -1}},
                   {"$limit": 20},
                   {"$project": {
                       "count_find": 0,
                       "find_job": 0
                   }},
                   {"$lookup": {
                       "from": "cv",
                       "localField": "_id",
                       "foreignField": "_id",
                       "as": "hashtag"
                   }},
                   {"$unwind": "$hashtag"},
                   {"$set": {
                       "_id": {"$toString": "$_id"},
                       "hashtag": "$hashtag.hashtag"
                   }}]
    return list(db.cv.aggregate(db_request))


def find_cv(id, attribute=None):
    if attribute is None:
        return db.cv.find_one({"_id": id})
    return db.cv.find_one({"_id": id}, attribute)


def check_skill(skills):
    for skill in skills:
        if skill.__class__ != dict:
            return False
        if not "skill" in skill or not "rate" in skill or len(skill)!=2:
            return False
        if skill["skill"].__class__!=str or skill["rate"].__class__!=int:
            return False
        if skill["rate"]>5 or skill["rate"]<1:
            return False
    return True


def check_content(contents):
    for content in contents:
        if content.__class__ != dict:
            return False
        if not "title" in content or not "content" in content or len(content) != 2:
            return False
        if content["title"].__class__!=str or content["content"].__class__!=list:
            return False
        if not check_content_block(content["content"]):
            return False
    return True


def check_content_block(contents):
    for content in contents:
        if content.__class__ != dict:
            return False
        if not "title" in content or not "position" in content or not "time" in content or not "detail" in content or len(content) != 4:
            return False
        if content["title"].__class__!=str or content["position"].__class__!=str or content["time"].__class__!=str or content["detail"].__class__!=str:
            return False
    return True


def create_cv(id_user, name, gender, avatar, position, dob, address, email, phone, place, skill, hashtag, content, interests):
    cv = CV(applicant=id_user)
    cv.name = name
    cv.gender = gender
    cv.avatar = avatar
    cv.position = position
    cv.dob = dob
    cv.address = address
    cv.email = email
    cv.phone = phone
    cv.place = place
    cv.skill = skill
    cv.hashtag = hashtag
    cv.content = content
    cv.interests = interests

    db.cv.insert_one(cv.__dict__)

    return cv.id()


def update_cv(id_cv, db_cv, name, gender, avatar, position, dob, address, email, phone, place, skill, hashtag, content, interests):
    cv = CV(dict=db_cv)
    cv.name = name
    cv.gender = gender
    cv.avatar = avatar
    cv.position = position
    cv.dob = dob
    cv.address = address
    cv.email = email
    cv.phone = phone
    cv.place = place
    cv.skill = skill
    cv.hashtag = hashtag
    cv.content = content
    cv.interests = interests

    db.cv.update_one({"_id": id_cv}, {"$set": cv.__dict__})


def delete_cv(id_cv):
    db.cv.delete_one({"_id": id_cv})


def get_list_cv_by_id_applicant(id_applicant, page):
    list_cv=list(db.cv.find({"applicant": id_applicant}, {"avatar":1, "hashtag": 1, "name": 1, "place": 1, "position": 1}).sort([("_id", -1)]).skip(page*10).limit(10))
    for cv in list_cv:
        cv["_id"]=str(cv["_id"])
    return list_cv


def get_number_cv_by_id_applicant(id_applicant):
    return math.ceil(db.cv.find({"applicant": id_applicant}).count() / 10)


def get_cv_admin(name, page, list_hashtag, place):
    request = [{"$match": {"name": {'$regex': name, '$options': 'i'}}}]

    if place != "":
        request += [{"$match": {"place": place}}]

    if len(list_hashtag) > 0:
        request += [{"$unwind": "$hashtag"},
                    {"$group": {
                        "_id": "$_id",
                        "name": {"$first": "$name"},
                        "place": {"$first": "$place"},
                        "hashtag": {"$addToSet": '$hashtag'},
                        "count_hashtag": {"$sum": 1}}
                    },
                    {"$unwind": "$hashtag"},
                    {"$match": {"hashtag": {"$in": list_hashtag}}},
                    {"$group": {
                        "_id": "$_id",
                        "name": {"$first": "$name"},
                        "place": {"$first": "$place"},
                        "count_hashtag": {"$first": "$count_hashtag"},
                        "count_find": {"$sum": 1}}
                    },
                    {"$match": {"count_find": {"$eq": len(list_hashtag)}}},
                    {"$sort": {"count_hashtag": 1, "_id": -1}},
                    {"$skip": page * 8},
                    {"$limit": 8},
                    {"$lookup": {
                        "from": "cv",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "hashtag"
                    }},
                    {"$project": {
                        "count_find": 0,
                        "count_hashtag": 0
                    }},
                    {"$unwind": "$hashtag"},
                    {"$set": {
                        "_id": {"$toString": "$_id"},
                        "hashtag": "$hashtag.hashtag"
                    }}]
    else:
        request += [{"$sort": {"_id": -1}},
                    {"$skip": page * 8},
                    {"$limit": 8},
                    {"$project": {
                        "_id": {"$toString": "$_id"},
                        "name": 1,
                        "place": 1,
                        "hashtag": 1
                    }}]

    return list(db.cv.aggregate(request))


def count_get_cv_admin(name, list_hashtag, place):
    request = [{"$match": {"name": {'$regex': name, '$options': 'i'}}}]

    if place != "":
        request += [{"$match": {"place": place}}]

    if len(list_hashtag) > 0:
        request += [{"$unwind": "$hashtag"},
                    {"$group": {
                        "_id": "$_id",
                        "name": {"$first": "$name"},
                        "place": {"$first": "$place"},
                        "hashtag": {"$addToSet": '$hashtag'},
                        "count_hashtag": {"$sum": 1}}
                    },
                    {"$unwind": "$hashtag"},
                    {"$match": {"hashtag": {"$in": list_hashtag}}},
                    {"$group": {
                        "_id": "$_id",
                        "name": {"$first": "$name"},
                        "place": {"$first": "$place"},
                        "count_hashtag": {"$first": "$count_hashtag"},
                        "count_find": {"$sum": 1}}
                    },
                    {"$match": {"count_find": {"$eq": len(list_hashtag)}}}]

    request += [{"$count": "count_page"}]

    data = list(db.cv.aggregate(request))

    if len(data) > 0:
        return math.ceil(data[0]["count_page"] / 8)
    else:
        return 0
