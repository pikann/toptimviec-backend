from flask import g, abort, request
from controller import bp, db, list_hashtag, list_place
from controller.auth import token_auth
from bson.objectid import ObjectId
import datetime
from model import Post
import threading


@bp.route('/post', methods=['GET'])
@token_auth.login_required(optional=True)
def get_list_post():
    rq = request.json
    if not rq or not 'list_id_showed' in rq or not 'list_hashtag' in rq or not 'place' in rq:
        abort(400)
    try:
        list_showed = [ObjectId(id_seen) for id_seen in rq["list_id_showed"]]

        if g.current_token is not None:
            token = g.current_token
            db_request = [{"$match": {"_id": token.id_user}},
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
            if rq["place"] != "":
                db_request += [{"$match": {"place": rq["place"]}}]

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
                               "employer.url": 0,
                               "count_find": 0,
                               "count_hashtag": 0
                           }},
                           {"$set": {
                               "employer._id": {"$toString": "$employer._id"},
                               "_id": {"$toString": "$_id"}
                           }}]
            list_post = list(db.applicant.aggregate(db_request))
            return {"list_post": list_post}
        else:
            db_request = [{"$match": {"_id": {"$not": {"$in": list_showed}}}},
                          {"$match": {"deadline": {"$gt": datetime.datetime.utcnow()}}}]
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


def learn_user_hashtag(id_user, post_hashtag):
    try:
        user = db.applicant.find_one({"_id": id_user})
        user_hashtag = user["hashtag"]
        hashtag = {}
        for h in post_hashtag:
            user_hashtag[h] += 1
        for h in user_hashtag:
            hashtag[h] = user_hashtag[h] * 10 / sum(user_hashtag.values())
        db.applicant.update_one({"_id": id_user}, {"$set": {"hashtag": hashtag}})
    except:
        pass


@bp.route('/post/<id>', methods=['GET'])
@token_auth.login_required(optional=True, role="applicant")
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
    except:
        abort(403)
    if len(post) == 0:
        abort(404)
    if g.current_token is not None:
        threading.Thread(target=learn_user_hashtag, args=(g.current_token.id_user, post[0]["hashtag"],)).start()
    return {"post": post[0]}


@bp.route('/post', methods=['POST'])
@token_auth.login_required(role="employer")
def post_post():
    token = g.current_token
    rq = request.json
    if not rq or not 'title' in rq or not 'description' in rq or not 'request' in rq or \
            not 'benefit' in rq or not 'place' in rq or not 'salary' in rq or \
            not 'deadline' in rq or not 'hashtag' in rq or not 'address' in rq:
        abort(400)
    if rq["title"].__class__ != str or rq["description"].__class__ != str or rq["request"].__class__ != str or rq[
        "benefit"].__class__ != str or rq["place"].__class__ != list or rq["salary"].__class__ != str or rq[
        "deadline"].__class__ != str or rq["hashtag"].__class__ != list or rq["address"].__class__ != str:
        abort(400)
    hashtag = [h for h in rq["hashtag"] if h in list_hashtag]
    place = [p for p in rq["place"] if p in list_place]

    if len(hashtag) == 0:
        abort(400)

    if len(place) == 0:
        abort(400)

    post = Post()
    post.title = rq["title"]
    post.description = rq["description"]
    post.request = rq["request"]
    post.benefit = rq["benefit"]
    post.place = place
    post.salary = rq["salary"]
    try:
        post.deadline = datetime.datetime.strptime(rq["deadline"], '%d/%m/%Y')
    except:
        abort(400)
    post.hashtag = hashtag
    post.address = rq["address"]
    post.employer = token.id_user

    try:
        db.post.insert_one(post.__dict__)
    except:
        abort(403)
    return {"id_post": str(post.id())}


@bp.route('/post/<id>', methods=['PUT'])
@token_auth.login_required()
def put_post(id):
    token = g.current_token
    try:
        db_post = db.post.find_one({"_id": ObjectId(id)})
    except:
        abort(403)

    if db_post is None:
        abort(404)

    if db_post["employer"] != token.id_user:
        abort(401)

    rq = request.json
    if not rq or not 'title' in rq or not 'description' in rq or not 'request' in rq or \
            not 'benefit' in rq or not 'place' in rq or not 'salary' in rq or \
            not 'deadline' in rq or not 'hashtag' in rq or not 'address' in rq:
        abort(400)
    if rq["title"].__class__ != str or rq["description"].__class__ != str or rq["request"].__class__ != str or rq[
        "benefit"].__class__ != str or rq["place"].__class__ != list or rq["salary"].__class__ != str or rq[
        "deadline"].__class__ != str or rq["hashtag"].__class__ != list or rq["address"].__class__ != str:
        abort(400)
    hashtag = [h for h in rq["hashtag"] if h in list_hashtag]
    place = [p for p in rq["place"] if p in list_place]

    if len(hashtag) == 0:
        abort(400)

    if len(place) == 0:
        abort(400)

    post = Post(db_post)
    post.title = rq["title"]
    post.description = rq["description"]
    post.request = rq["request"]
    post.benefit = rq["benefit"]
    post.place = place
    post.salary = rq["salary"]
    try:
        post.deadline = datetime.datetime.strptime(rq["deadline"], '%d/%m/%Y')
    except:
        abort(400)
    post.hashtag = hashtag
    post.address = rq["address"]

    try:
        db.post.update_one({"_id": ObjectId(id)}, {"$set": post.__dict__})
    except:
        abort(403)

    return "ok"


@bp.route('/post/<id>', methods=['DELETE'])
@token_auth.login_required()
def delete_post(id):
    token = g.current_token
    try:
        db_post = db.post.find_one({"_id": ObjectId(id)}, {"_id": 0, "employer": 1})
    except:
        abort(403)

    if db_post is None:
        abort(404)

    if db_post["employer"] != token.id_user:
        abort(401)

    db.post.delete_one({"_id": ObjectId(id)})
    return "ok"


if __name__ == "__main__":
    learn_user_hashtag(ObjectId("6020c6f780407c6f5796325f"), ["Java"])
