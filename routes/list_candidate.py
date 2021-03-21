from flask import g, abort, request
from routes import bp, db
from routes.auth import token_auth
from bson.objectid import ObjectId
from models.List_Candidate import List_Candidate


def new_candidate_list_for_post(name, id_user):
    list_candidate = List_Candidate(id_user)
    list_candidate.name = name
    try:
        db.list_candidate.insert_one(list_candidate.__dict__)
    except:
        pass


@bp.route('/list-candidate', methods=['POST'])
@token_auth.login_required(role="employer")
def new_candidate_list():
    token = g.current_token
    rq = request.json
    if not rq or not 'name' in rq:
        abort(400)
    if rq["name"].__class__!=str:
        abort(400)
    list_candidate=List_Candidate(token.id_user)
    list_candidate.name=rq["name"]
    try:
        db.list_candidate.insert_one(list_candidate.__dict__)
    except:
        abort(403)
    return {"id": str(list_candidate.id())}


@bp.route('/list-candidate', methods=['GET'])
@token_auth.login_required(role="employer")
def get_my_candidate_lists():
    global page
    token = g.current_token
    try:
        page = int(request.args.get('page', default=0))
    except:
        abort(400)
    try:
        candidate_lists=list(db.list_candidate.find({"employer": token.id_user}, {"_id": 1, "name": 1}).sort([("_id", -1)]).skip(page*10).limit(10))
        for candidate_list in candidate_lists:
            candidate_list["_id"]=str(candidate_list["_id"])
        return {"candidate_lists": candidate_lists}
    except:
        abort(403)


@bp.route('/list-candidate/<id>/add/<id_cv>', methods=['POST'])
@token_auth.login_required(role="employer")
def add_cv_to_list(id, id_cv):
    token = g.current_token
    try:
        db.list_candidate.update({"_id": ObjectId(id), "employer": token.id_user}, {"$addToSet": {"list": ObjectId(id_cv)}})
    except:
        abort(403)
    return "ok"


@bp.route('/list-candidate/<id>', methods=['GET'])
@token_auth.login_required(role="employer")
def get_my_candidate_list(id):
    global candidate_list
    token = g.current_token
    try:
        candidate_list = db.list_candidate.find_one({"_id": ObjectId(id), "employer": token.id_user})
        if len(candidate_list["list"])==0:
            return {"_id": str(candidate_list["_id"]), "name": candidate_list["name"], "list": candidate_list["list"]}
        candidate_list = list(db.list_candidate.aggregate([{"$match": {"_id": ObjectId(id), "employer": token.id_user}},
                                                        {"$unwind": "$list"},
                                                        {"$lookup": {
                                                            "from": "cv",
                                                            "localField": "list",
                                                            "foreignField": "_id",
                                                            "as": "list"
                                                        }},
                                                        {"$unwind": "$list"},
                                                        {"$set": {
                                                            "list._id": {"$toString": "$list._id"}
                                                        }},
                                                        {"$group": {
                                                          "_id": "$_id",
                                                          "name": {"$first": "$name"},
                                                          "list": {"$push": "$list"}
                                                        }},
                                                        {"$project": {
                                                            "_id": 1,
                                                            "name": 1,
                                                            "list._id": 1,
                                                            "list.name": 1,
                                                            "list.avatar": 1,
                                                            "list.position": 1,
                                                            "list.hashtag": 1,
                                                            "list.place": 1
                                                        }},
                                                        {"$set": {
                                                            "_id": {"$toString": "$_id"}
                                                        }}]))[0]
    except:
        abort(404)
    return candidate_list


@bp.route('/list-candidate/<id>', methods=['PUT'])
@token_auth.login_required(role="employer")
def change_name_list_candidate(id):
    token = g.current_token
    rq = request.json
    if not rq or not 'name' in rq:
        abort(400)
    if rq["name"].__class__ != str:
        abort(400)
    try:
        db.list_candidate.update_one({"_id": ObjectId(id), "employer": token.id_user}, {"$set": {"name": rq["name"]}})
    except:
        abort(404)
    return "ok"


@bp.route('/list-candidate/<id>', methods=['DELETE'])
@token_auth.login_required(role="employer")
def delete_list_candidate(id):
    global db_post, rs
    token = g.current_token
    try:
        rs=db.list_candidate.delete_one({"_id": ObjectId(id), "employer": token.id_user})
    except:
        abort(403)
    if rs.deleted_count==0:
        abort(404)
    return "ok"


@bp.route('/list-candidate/<id>/<id_cv>', methods=['DELETE'])
@token_auth.login_required(role="employer")
def delete_cv_from_list_candidate(id, id_cv):
    token = g.current_token
    try:
        rs=db.list_candidate.update_one({"_id": ObjectId(id), "employer": token.id_user}, {"$pull": {"list": ObjectId(id_cv)}})
    except:
        abort(403)
    if rs.modified_count==0:
        abort(404)
    return "ok"


