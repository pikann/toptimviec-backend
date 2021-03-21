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


def find_cv(id, attribute={}):
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


def create_cv(id_user, name, gender, avatar, position, dob, address, email, phone, place, skill, hashtag, content, interests, find_job):
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
    cv.find_job = find_job

    db.cv.insert_one(cv.__dict__)

    return cv.id()


def update_cv(id_cv, db_cv, name, gender, avatar, position, dob, address, email, phone, place, skill, hashtag, content, interests, find_job):
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
    cv.find_job = find_job

    db.cv.update_one({"_id": id_cv}, {"$set": cv.__dict__})


def delete_cv(id_cv):
    db.cv.delete_one({"_id": id_cv})