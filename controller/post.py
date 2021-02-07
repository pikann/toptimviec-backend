from flask import g, abort, request
from controller import bp, db
from controller.auth import token_auth
from bson.objectid import ObjectId


@bp.route('/post', methods=['GET'])
@token_auth.login_required(optional=True)
def get_list_post():
    rq = request.json
    if not rq or not 'list_id_showed' in rq or not 'list_hashtag' in rq or not 'place' in rq:
        abort(400)
    try:
        list_showed = [ObjectId(id_seen) for id_seen in rq["list_id_showed"]]

        db_request = [{"$match": {"_id": {"$not": {"$in": list_showed}}}}]
        if rq["place"] != "":
            db_request += [{"$match": {"place": rq["place"]}}]
        if len(rq["list_hashtag"]) > 0:
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
                           {"$match": {"hashtag": {"$in": rq["list_hashtag"]}}},
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
                           {"$limit": 20},
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
                               "employer.url": 0,
                               "count_find": 0
                           }},
                           {"$unwind": "$hashtag"},
                           {"$set": {
                               "employer._id": {"$toString": "$employer._id"},
                               "_id": {"$toString": "$_id"},
                               "hashtag": "$hashtag.hashtag"
                           }}]
        else:
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
                               "employer.bio": 0,
                               "employer.url": 0
                           }},
                           {"$set": {
                               "employer._id": {"$toString": "$employer._id"}
                           }}]

        list_post = list(db.post.aggregate(db_request))
        return {"list_post": list_post}
    except:
        abort(403)


@bp.route('/post/<id>', methods=['GET'])
@token_auth.login_required(optional=True)
def get_post(id):
    try:
        post = list(db.post.aggregate([{"$match": {"_id": ObjectId(id)}},
                                       {"$lookup": {
                                           "from": "employer",
                                           "localField": "employer",
                                           "foreignField": "_id",
                                           "as": "employer"
                                       }},
                                       {"$unwind": "$employer"},
                                       {"$project": {
                                           "url": 0,
                                           "employer.url": 0,
                                           "employer.bio": 0
                                       }},
                                       {"$set": {
                                           "employer._id": {"$toString": "$employer._id"},
                                           "_id": {"$toString": "$_id"}
                                       }}]))
        return {"post": post[0]}
    except:
        abort(403)