from flask import g, abort, request
from routes import bp
from services.auth import token_auth
from bson.objectid import ObjectId
from services.list_candidate import create_candidate_list, get_list_my_list_candidate, add_candidate, \
    get_candidate_list, update_list_name, delete_list, remove_candidate, count_page_list_my_list_candidate


@bp.route('/list-candidate', methods=['POST'])
@token_auth.login_required(role="employer")
def new_candidate_list():
    global id_list
    token = g.current_token
    rq = request.json
    if not rq or not 'name' in rq:
        abort(400)
    if rq["name"].__class__ != str:
        abort(400)
    try:
        id_list = create_candidate_list(token.id_user, rq["name"])
    except:
        abort(403)
    return {"id": str(id_list)}


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
        candidate_lists = get_list_my_list_candidate(token.id_user, page)
        for candi_list in candidate_lists:
            candi_list["_id"] = str(candi_list["_id"])
        count = count_page_list_my_list_candidate(token.id_user)
        return {"candidate_lists": candidate_lists, "page": count}
    except:
        abort(403)


@bp.route('/list-candidate/<id>/add/<id_cv>', methods=['POST'])
@token_auth.login_required(role="employer")
def add_cv_to_list(id, id_cv):
    token = g.current_token
    try:
        add_candidate(ObjectId(id), token.id_user, ObjectId(id_cv))
    except:
        abort(403)
    return "ok"


@bp.route('/list-candidate/<id>', methods=['GET'])
@token_auth.login_required(role="employer")
def get_my_candidate_list(id):
    global candidate_list
    token = g.current_token
    try:
        candidate_list = get_candidate_list(ObjectId(id), token.id_user)
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
        update_list_name(ObjectId(id), token.id_user, rq["name"])
    except:
        abort(404)
    return "ok"


@bp.route('/list-candidate/<id>', methods=['DELETE'])
@token_auth.login_required(role="employer")
def delete_list_candidate(id):
    global db_post, rs
    token = g.current_token
    try:
        rs = delete_list(ObjectId(id), token.id_user)
    except:
        abort(403)
    if rs.deleted_count == 0:
        abort(404)
    return "ok"


@bp.route('/list-candidate/<id>/<id_cv>', methods=['DELETE'])
@token_auth.login_required(role="employer")
def delete_cv_from_list_candidate(id, id_cv):
    global rs
    token = g.current_token
    try:
        rs = remove_candidate(ObjectId(id), token.id_user, ObjectId(id_cv))
    except:
        abort(403)
    if rs.modified_count == 0:
        abort(404)
    return "ok"
