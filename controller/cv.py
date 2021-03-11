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


@bp.route('/cv', methods=['POST'])
@token_auth.login_required(role="applicant")
def post_cv():
    token = g.current_token
    rq = request.json
    if not rq or not 'name' in rq or not 'gender' in rq or not 'avatar' in rq or \
            not 'position' in rq or not 'dob' in rq or not 'address' in rq or \
            not 'email' in rq or not 'phone' in rq or not 'place' in rq or not 'skill' in rq or\
            not 'hashtag' in rq or not 'content' in rq or not 'interests' in rq or not 'find_job' in rq:
        abort(400)
    if rq["name"].__class__ != str or rq["gender"].__class__ != bool or rq["avatar"].__class__ != str or rq[
        "position"].__class__ != str or rq["dob"].__class__ != str or rq["address"].__class__ != str or rq[
        "email"].__class__ != str or rq["phone"].__class__ != str or rq["place"].__class__ != str or rq[
        "skill"].__class__ != list or rq["hashtag"].__class__ != list or rq["content"].__class__ != list or rq[
        "interests"].__class__ != list or rq["find_job"].__class__ != bool:
        abort(400)
    hashtag = [h for h in rq["hashtag"] if h in list_hashtag]
    if rq["place"] not in list_place:
        abort(400, 'Error 400: Place not exist')
    if len(hashtag)==0:
        abort(400, 'Error 400: Hashtag not exist')
    if not CV.check_skill(rq["skill"]):
        abort(400, 'Error 400: Skill is not in the correct format')
    if not CV.check_content(rq["content"]):
        abort(400, 'Error 400: Content is not in the correct format')
    for interest in rq["interests"]:
        if interest.__class__!=str:
            abort(400)
    cv=CV(applicant=token.id_user)
    cv.name=rq["name"]
    cv.gender=rq["gender"]
    cv.avatar=rq["avatar"]
    cv.position=rq["position"]
    try:
        cv.dob = datetime.datetime.strptime(rq["dob"], '%d/%m/%Y')
    except:
        abort(400, 'Error 400: Day of birth is not in the correct format')
    cv.address=rq["address"]
    cv.email=rq["email"]
    cv.phone=rq["phone"]
    cv.place=rq["place"]
    cv.skill=rq["skill"]
    cv.hashtag=hashtag
    cv.content=rq["content"]
    cv.interests=rq["interests"]
    cv.find_job=rq["find_job"]

    try:
        db.cv.insert_one(cv.__dict__)
    except:
        abort(403)
    return {"id_cv": str(cv.id())}

@bp.route('/cv/<id>', methods=['PUT'])
@token_auth.login_required()
def put_cv(id):
    token = g.current_token
    try:
        db_cv = db.cv.find_one({"_id": ObjectId(id)})
    except:
        abort(403)

    if db_cv is None:
        abort(404)

    if db_cv["applicant"] != token.id_user:
        abort(405)

    rq = request.json
    if not rq or not 'name' in rq or not 'gender' in rq or not 'avatar' in rq or \
            not 'position' in rq or not 'dob' in rq or not 'address' in rq or \
            not 'email' in rq or not 'phone' in rq or not 'place' in rq or not 'skill' in rq or\
            not 'hashtag' in rq or not 'content' in rq or not 'interests' in rq or not 'find_job' in rq:
        abort(400)
    if rq["name"].__class__ != str or rq["gender"].__class__ != bool or rq["avatar"].__class__ != str or rq[
        "position"].__class__ != str or rq["dob"].__class__ != str or rq["address"].__class__ != str or rq[
        "email"].__class__ != str or rq["phone"].__class__ != str or rq["place"].__class__ != str or rq[
        "skill"].__class__ != list or rq["hashtag"].__class__ != list or rq["content"].__class__ != list or rq[
        "interests"].__class__ != list or rq["find_job"].__class__ != bool:
        abort(400)
    hashtag = [h for h in rq["hashtag"] if h in list_hashtag]
    if rq["place"] not in list_place:
        abort(400, 'Error 400: Place not exist')
    if len(hashtag)==0:
        abort(400, 'Error 400: Hashtag not exist')
    if not CV.check_skill(rq["skill"]):
        abort(400, 'Error 400: Skill is not in the correct format')
    if not CV.check_content(rq["content"]):
        abort(400, 'Error 400: Content is not in the correct format')
    for interest in rq["interests"]:
        if interest.__class__!=str:
            abort(400)
    cv=CV(dict=db_cv)
    cv.name=rq["name"]
    cv.gender=rq["gender"]
    cv.avatar=rq["avatar"]
    cv.position=rq["position"]
    try:
        cv.dob = datetime.datetime.strptime(rq["dob"], '%d/%m/%Y')
    except:
        abort(400, 'Error 400: Day of birth is not in the correct format')
    cv.address=rq["address"]
    cv.email=rq["email"]
    cv.phone=rq["phone"]
    cv.place=rq["place"]
    cv.skill=rq["skill"]
    cv.hashtag=hashtag
    cv.content=rq["content"]
    cv.interests=rq["interests"]
    cv.find_job=rq["find_job"]

    try:
        db.cv.update_one({"_id": ObjectId(id)}, {"$set": cv.__dict__})
    except:
        abort(403)
    return "ok"

@bp.route('/cv/<id>', methods=['DELETE'])
@token_auth.login_required()
def delete_cv(id):
    token = g.current_token
    try:
        db_cv = db.cv.find_one({"_id": ObjectId(id)}, {"_id": 0, "applicant": 1})
    except:
        abort(403)

    if db_cv is None:
        abort(404)

    if db_cv["applicant"] != token.id_user:
        abort(405)

    db.cv.delete_one({"_id": ObjectId(id)})
    return "ok"