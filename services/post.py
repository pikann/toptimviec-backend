import math
from services import db
import datetime
from models.Post import Post


def get_post_of_employer(id, page):
    list_post = list(db.post.aggregate([{"$match": {"employer": id}},
                                        {"$sort": {"_id": -1}},
                                        {"$skip": page * 20},
                                        {"$limit": 20},
                                        {"$project": {
                                            "_id": {"$toString": "$_id"},
                                            "title": 1,
                                            "employer": 1,
                                            "place": 1,
                                            "hashtag": 1,
                                            "salary": 1
                                        }},
                                        {"$lookup": {
                                            "from": "employer",
                                            "localField": "employer",
                                            "foreignField": "_id",
                                            "as": "employer"
                                        }},
                                        {"$unwind": "$employer"},
                                        {"$project": {
                                            "employer.bio": 0,
                                            "employer.hashtag": 0
                                        }},
                                        {"$set": {
                                            "employer._id": {"$toString": "$employer._id"}
                                        }}]))
    return list_post


def count_page_my_list_post(id):
    return math.ceil(db.post.find({"employer": id}).count() / 20)


def recommend_post(id_user, list_showed, place):
    db_request = [{"$match": {"_id": id_user}},
                  {"$project": {"hashtag": {"$objectToArray": "$hashtag"}, "_id": 0}},
                  {"$unwind": "$hashtag"},
                  {"$lookup": {
                      "from": "post",
                      "localField": "hashtag.k",
                      "foreignField": "hashtag",
                      "as": "post"
                  }
                  },
                  {"$unwind": "$post"},
                  {"$group": {
                      "_id": "$post._id",
                      "title": {"$first": "$post.title"},
                      "employer": {"$first": "$post.employer"},
                      "place": {"$first": "$post.place"},
                      "salary": {"$first": "$post.salary"},
                      "hashtag": {"$first": "$post.hashtag"},
                      "deadline": {"$first": "$post.deadline"},
                      "count_find": {"$sum": "$hashtag.v"}
                  }},
                  {"$match": {"_id": {"$not": {"$in": list_showed}}}},
                  {"$match": {"deadline": {"$gt": datetime.datetime.utcnow()}}}]
    if place != "":
        db_request += [{"$match": {"place": place}}]

    db_request += [{"$unwind": "$hashtag"},
                   {"$group": {
                       "_id": "$_id",
                       "title": {"$first": "$title"},
                       "employer": {"$first": "$employer"},
                       "place": {"$first": "$place"},
                       "salary": {"$first": "$salary"},
                       "hashtag": {"$addToSet": '$hashtag'},
                       "count_find": {"$first": "$count_find"},
                       "count_hashtag": {"$sum": 1}}
                   },
                   {"$sort": {"count_find": -1, "_id": -1}},
                   {"$limit": 20},
                   {"$lookup": {
                       "from": "employer",
                       "localField": "employer",
                       "foreignField": "_id",
                       "as": "employer"
                   }},
                   {"$unwind": "$employer"},
                   {"$project": {
                       "employer.bio": 0,
                       "count_find": 0,
                       "count_hashtag": 0
                   }},
                   {"$set": {
                       "employer._id": {"$toString": "$employer._id"},
                       "_id": {"$toString": "$_id"}
                   }}]
    return list(db.applicant.aggregate(db_request))


def search_post(list_showed, place, hashtag, limit=20):
    db_request = [{"$match": {"_id": {"$not": {"$in": list_showed}}}},
                  {"$match": {"deadline": {"$gt": datetime.datetime.utcnow()}}}]
    if place != "":
        db_request += [{"$match": {"place": place}}]
    db_request += [{"$unwind": "$hashtag"},
                   {"$group": {
                       "_id": "$_id",
                       "title": {"$first": "$title"},
                       "employer": {"$first": "$employer"},
                       "place": {"$first": "$place"},
                       "salary": {"$first": "$salary"},
                       "hashtag": {"$addToSet": '$hashtag'},
                       "count_hashtag": {"$sum": 1}}
                   },
                   {"$unwind": "$hashtag"},
                   {"$match": {"hashtag": {"$in": hashtag}}},
                   {"$group": {
                       "_id": "$_id",
                       "title": {"$first": "$title"},
                       "employer": {"$first": "$employer"},
                       "place": {"$first": "$place"},
                       "salary": {"$first": "$salary"},
                       "count_hashtag": {"$first": "$count_hashtag"},
                       "count_find": {"$sum": 1}}
                   },
                   {"$sort": {"count_find": -1, "count_hashtag": 1, "_id": -1}},
                   {"$limit": limit},
                   {"$lookup": {
                       "from": "employer",
                       "localField": "employer",
                       "foreignField": "_id",
                       "as": "employer"
                   }},
                   {"$lookup": {
                       "from": "post",
                       "localField": "_id",
                       "foreignField": "_id",
                       "as": "hashtag"
                   }},
                   {"$unwind": "$employer"},
                   {"$project": {
                       "employer.bio": 0,
                       "count_find": 0
                   }},
                   {"$unwind": "$hashtag"},
                   {"$set": {
                       "employer._id": {"$toString": "$employer._id"},
                       "_id": {"$toString": "$_id"},
                       "hashtag": "$hashtag.hashtag"
                   }}]
    return list(db.post.aggregate(db_request))


def get_all_post(list_showed, place):
    db_request = [{"$match": {"_id": {"$not": {"$in": list_showed}}}},
                  {"$match": {"deadline": {"$gt": datetime.datetime.utcnow()}}}]
    if place != "":
        db_request += [{"$match": {"place": place}}]
    db_request += [{"$sort": {"_id": -1}},
                   {"$limit": 20},
                   {"$project": {
                       "_id": {"$toString": "$_id"},
                       "title": 1,
                       "employer": 1,
                       "place": 1,
                       "hashtag": 1,
                       "salary": 1
                   }},
                   {"$lookup": {
                       "from": "employer",
                       "localField": "employer",
                       "foreignField": "_id",
                       "as": "employer"
                   }},
                   {"$unwind": "$employer"},
                   {"$project": {
                       "employer.bio": 0
                   }},
                   {"$set": {
                       "employer._id": {"$toString": "$employer._id"}
                   }}]
    return list(db.post.aggregate(db_request))


def get_post_info(id_post):
    post = list(db.post.aggregate([{"$match": {"_id": id_post}},
                                   {"$lookup": {
                                       "from": "employer",
                                       "localField": "employer",
                                       "foreignField": "_id",
                                       "as": "employer"
                                   }},
                                   {"$unwind": "$employer"},
                                   {"$set": {
                                       "employer._id": {"$toString": "$employer._id"},
                                       "_id": {"$toString": "$_id"}
                                   }}]))
    if len(post) == 0:
        return None
    rs = post[0]
    if len(rs["employer"]["bio"]) > 250:
        rs["employer"]["bio"] = rs["employer"]["bio"][:250] + "..."
    rs["recommend"] = search_post([rs["_id"]], rs["place"], rs["hashtag"], 10)
    return rs


def new_post(title, description, request, benefit, place, salary, deadline, hashtag, address, id_user):
    post = Post()
    post.title = title
    post.description = description
    post.request = request
    post.benefit = benefit
    post.place = place
    post.salary = salary
    post.deadline = deadline
    post.hashtag = hashtag
    post.address = address
    post.employer = id_user

    db.post.insert_one(post.__dict__)

    return post.id()


def find_post(id_post, attribute=None):
    if attribute is None:
        return db.post.find_one({"_id": id_post})
    return db.post.find_one({"_id": id_post}, attribute)


def update_post(db_post, id_post, title, description, request, benefit, place, salary, deadline, hashtag, address):
    post = Post(db_post)
    post.title = title
    post.description = description
    post.request = request
    post.benefit = benefit
    post.place = place
    post.salary = salary
    post.deadline = deadline
    post.hashtag = hashtag
    post.address = address

    db.post.update_one({"_id": id_post}, {"$set": post.__dict__})


def delete_post_by_id(id_post):
    db.post.delete_one({"_id": id_post})


def get_post_admin(title, page, list_hashtag, place):
    request = [{"$match": {"title": {'$regex': title, '$options': 'i'}}},
               {"$match": {"deadline": {"$gt": datetime.datetime.utcnow()}}}]

    if place != "":
        request += [{"$match": {"place": place}}]

    request += [{"$unwind": "$hashtag"},
                {"$group": {
                    "_id": "$_id",
                    "title": {"$first": "$title"},
                    "employer": {"$first": "$employer"},
                    "place": {"$first": "$place"},
                    "salary": {"$first": "$salary"},
                    "hashtag": {"$addToSet": '$hashtag'},
                    "count_hashtag": {"$sum": 1}}
                },
                {"$unwind": "$hashtag"},
                {"$match": {"hashtag": {"$in": list_hashtag}}},
                {"$group": {
                    "_id": "$_id",
                    "title": {"$first": "$title"},
                    "employer": {"$first": "$employer"},
                    "place": {"$first": "$place"},
                    "salary": {"$first": "$salary"},
                    "count_hashtag": {"$first": "$count_hashtag"},
                    "count_find": {"$sum": 1}}
                },
                {"$match": {"count_find": {"$eq": len(list_hashtag)}}},
                {"$sort": {"count_find": -1, "count_hashtag": 1, "_id": -1}},
                {"$skip": page * 8},
                {"$limit": 8},
                {"$lookup": {
                    "from": "employer",
                    "localField": "employer",
                    "foreignField": "_id",
                    "as": "employer"
                }},
                {"$lookup": {
                    "from": "post",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "hashtag"
                }},
                {"$unwind": "$employer"},
                {"$project": {
                    "count_find": 0,
                    "count_hashtag": 0,
                    "salary": 0
                }},
                {"$unwind": "$hashtag"},
                {"$set": {
                    "_id": {"$toString": "$_id"},
                    "hashtag": "$hashtag.hashtag",
                    "employer": "$employer.name"
                }}]

    return list(db.post.aggregate(request))


def count_get_post_admin(title, list_hashtag, place):
    request = [{"$match": {"title": {'$regex': title, '$options': 'i'}}},
               {"$match": {"deadline": {"$gt": datetime.datetime.utcnow()}}}]

    if place != "":
        request += [{"$match": {"place": place}}]

    request += [{"$unwind": "$hashtag"},
                {"$group": {
                    "_id": "$_id",
                    "title": {"$first": "$title"},
                    "employer": {"$first": "$employer"},
                    "place": {"$first": "$place"},
                    "salary": {"$first": "$salary"},
                    "hashtag": {"$addToSet": '$hashtag'},
                    "count_hashtag": {"$sum": 1}}
                },
                {"$unwind": "$hashtag"},
                {"$match": {"hashtag": {"$in": list_hashtag}}},
                {"$group": {
                    "_id": "$_id",
                    "title": {"$first": "$title"},
                    "employer": {"$first": "$employer"},
                    "place": {"$first": "$place"},
                    "salary": {"$first": "$salary"},
                    "count_hashtag": {"$first": "$count_hashtag"},
                    "count_find": {"$sum": 1}}
                },
                {"$match": {"count_find": {"$eq": len(list_hashtag)}}},
                {"$count": "count_page"}]

    return math.ceil(list(db.post.aggregate(request))[0]["count_page"] / 8)
