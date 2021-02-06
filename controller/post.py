from flask import g, abort, request
from controller import bp, db
from controller.auth import token_auth
from bson.objectid import ObjectId


@bp.route('/post', methods=['GET'])
@token_auth.login_required(optional=True)
def get_list_post():
    rq = request.json
    if not rq or not 'list_id_showed' in rq:
        abort(400)
    try:
        list_showed = [ObjectId(id_seen) for id_seen in rq["list_id_showed"]]

        list_post = list(db.post.aggregate([{"$match": {"_id": {"$not": {"$in": list_showed}}}},
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
