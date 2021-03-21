from flask import request, abort
from routes import bp
import re
from bson.objectid import ObjectId
from services.user import check_email
from services.employer import create_employer, find_employer


@bp.route("/employer", methods=['POST'])
def post_employer():
    rq = request.json
    if not rq or not 'email' in rq or not 'password' in rq or not "name" in rq:
        abort(400)

    if not re.match(r"[-a-zA-Z0-9.`?{}]+@\w+\.\w+", rq["email"]):
        abort(400)

    if not check_email(rq["email"]):
        abort(409)

    try:
        create_employer(rq['email'], rq['password'], rq['name'])
    except:
        abort(400)

    return "ok", 201


@bp.route("/employer/<id>", methods=['GET'])
def get_employer(id):
    global employer
    try:
        employer = find_employer(ObjectId(id))
    except:
        abort(403)
    return employer


@bp.route("/employer/<id>/post", methods=['GET'])
def get_post_employer(id):
    rq = request.json
    if not rq or not 'list_id_showed' in rq:
        abort(400)
    try:
        list_showed = [ObjectId(id_seen) for id_seen in rq["list_id_showed"]]
        list_post = list(db.post.aggregate([{"$match": {"_id": {"$not": {"$in": list_showed}}}},
                                            {"$match": {"employer": ObjectId(id)}},
                                            {"$sort": {"_id": -1}},
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
                                            }}]))
        return {"list_post": list_post}
    except:
        abort(403)
