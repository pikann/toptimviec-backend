from flask import g, abort, request
from controller import bp, db, list_hashtag, list_place
from controller.auth import token_auth
from bson.objectid import ObjectId
import datetime
from model import CV
import threading


@bp.route('/cv', methods=['GET'])
@token_auth.login_required()
def get_list_cv():
    try:
        list_showed = [ObjectId(s.strip()) for s in request.args.get('list-id-showed', default="").split(',') if
                       len(s.strip()) > 0]
        hashtag = [s.strip() for s in request.args.get('list-hashtag', default="").split(',') if len(s.strip()) > 0]
        place = request.args.get('place', default="")
    except:
        abort(400)
    if len(hashtag) == 0:
        token = g.current_token
        db_request = [{"$match": {"_id": token.id_user}},
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
        list_cv = list(db.employer.aggregate(db_request))
        return {"list_cv": list_cv}
    else:
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
        list_cv = list(db.cv.aggregate(db_request))
        return {"list_cv": list_cv}


def learn_employer_hashtag(id_user, cv_hashtag):
    try:
        user = db.employer.find_one({"_id": id_user})
        user_hashtag = user["hashtag"]
        hashtag = {}
        for h in cv_hashtag:
            user_hashtag[h] += 1
        for h in user_hashtag:
            hashtag[h] = user_hashtag[h] * 10 / sum(user_hashtag.values())
        db.employer.update_one({"_id": id_user}, {"$set": {"hashtag": hashtag}})
    except:
        pass



@bp.route('/cv/<id>', methods=['GET'])
@token_auth.login_required()
def get_cv(id):
    token=g.current_token
    try:
        cv=db.cv.find_one({"_id": ObjectId(id)}, {"_id": 0, "find_job": 0})
    except:
        abort(403)
    if cv is None:
        abort(404)
    if token.role=="employer":
        threading.Thread(target=learn_employer_hashtag, args=(g.current_token.id_user, cv["hashtag"],)).start()
    elif token.role=="applicant":
        if cv["applicant"]!=token.id_user:
            abort(405)
    cv.pop("applicant", None)
    return cv