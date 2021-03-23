from flask import g, abort, request
from routes import bp
from services.auth import token_auth
from bson.objectid import ObjectId
import datetime
import threading
from services.learn import learn_applicant_hashtag, learn_employer_hashtag
from services.global_data import check_list_hashtag, check_place
from services.cv import recommend_cv, find_list_cv, find_cv, check_skill, check_content, create_cv, update_cv, delete_cv, get_list_cv_by_id_applicant


@bp.route('/cv-list', methods=['POST'])
@token_auth.login_required(role="employer")
def get_list_cv():
    global place, list_showed, hashtag
    rq = request.json
    if not rq or not 'list_id_showed' in rq or not 'list_hashtag' in rq or not 'place' in rq:
        abort(400)
    if rq["list_id_showed"].__class__ != list or rq["list_hashtag"].__class__ != list or rq["place"].__class__ != str:
        abort(400)
    try:
        list_showed = [ObjectId(s) for s in rq["list_id_showed"]]
        hashtag = check_list_hashtag(rq["list_hashtag"])
        place = check_place(rq["place"])
    except:
        abort(400)
    if len(hashtag) == 0:
        token = g.current_token
        list_cv = recommend_cv(token.id_user, list_showed, place)
        return {"list_cv": list_cv}
    else:
        list_cv = find_list_cv(list_showed, hashtag, place)
        return {"list_cv": list_cv}


@bp.route('/cv/<id>', methods=['GET'])
@token_auth.login_required()
def get_cv(id):
    global cv
    token = g.current_token
    try:
        cv = find_cv(ObjectId(id), {"_id": 0, "find_job": 0})
    except:
        abort(403)
    if cv is None:
        abort(404)
    if token.role == "employer":
        threading.Thread(target=learn_employer_hashtag, args=(g.current_token.id_user, cv["hashtag"],)).start()
    elif token.role == "applicant":
        if cv["applicant"] != token.id_user:
            abort(405)
    cv.pop("applicant", None)
    return cv


@bp.route('/cv', methods=['POST'])
@token_auth.login_required(role="applicant")
def post_cv():
    global dob, id_cv
    token = g.current_token
    rq = request.json
    if not rq or not 'name' in rq or not 'gender' in rq or not 'avatar' in rq or \
            not 'position' in rq or not 'dob' in rq or not 'address' in rq or \
            not 'email' in rq or not 'phone' in rq or not 'place' in rq or not 'skill' in rq or \
            not 'hashtag' in rq or not 'content' in rq or not 'interests' in rq or not 'find_job' in rq:
        abort(400)
    if rq["name"].__class__ != str or rq["gender"].__class__ != bool or rq["avatar"].__class__ != str or rq[
        "position"].__class__ != str or rq["dob"].__class__ != str or rq["address"].__class__ != str or rq[
        "email"].__class__ != str or rq["phone"].__class__ != str or rq["place"].__class__ != str or rq[
        "skill"].__class__ != list or rq["hashtag"].__class__ != list or rq["content"].__class__ != list or rq[
        "interests"].__class__ != list or rq["find_job"].__class__ != bool:
        abort(400)
    hashtag = check_list_hashtag(rq["hashtag"])
    if check_place(rq["place"]) == "":
        abort(400, 'Error 400: Place not exist')
    if len(hashtag) == 0:
        abort(400, 'Error 400: Hashtag not exist')
    if not check_skill(rq["skill"]):
        abort(400, 'Error 400: Skill is not in the correct format')
    if not check_content(rq["content"]):
        abort(400, 'Error 400: Content is not in the correct format')
    for interest in rq["interests"]:
        if interest.__class__ != str:
            abort(400)
    try:
        dob = datetime.datetime.strptime(rq["dob"], '%d/%m/%Y')
    except:
        abort(400, 'Error 400: Day of birth is not in the correct format')
    try:
        id_cv=create_cv(token.id_user, rq["name"], rq["gender"], rq["avatar"], rq["position"], dob, rq["address"], rq["email"], rq["phone"], rq["place"], rq["skill"], hashtag, rq["content"], rq["interests"], rq["find_job"])
    except:
        abort(403)

    threading.Thread(target=learn_applicant_hashtag, args=(g.current_token.id_user, hashtag,)).start()

    return {"id_cv": str(id_cv)}


@bp.route('/cv/<id>', methods=['PUT'])
@token_auth.login_required()
def put_cv(id):
    global db_cv
    token = g.current_token
    try:
        db_cv = find_cv(ObjectId(id))
    except:
        abort(403)

    if db_cv is None:
        abort(404)

    if db_cv["applicant"] != token.id_user:
        abort(405)

    rq = request.json
    if not rq or not 'name' in rq or not 'gender' in rq or not 'avatar' in rq or \
            not 'position' in rq or not 'dob' in rq or not 'address' in rq or \
            not 'email' in rq or not 'phone' in rq or not 'place' in rq or not 'skill' in rq or \
            not 'hashtag' in rq or not 'content' in rq or not 'interests' in rq or not 'find_job' in rq:
        abort(400)
    if rq["name"].__class__ != str or rq["gender"].__class__ != bool or rq["avatar"].__class__ != str or rq[
        "position"].__class__ != str or rq["dob"].__class__ != str or rq["address"].__class__ != str or rq[
        "email"].__class__ != str or rq["phone"].__class__ != str or rq["place"].__class__ != str or rq[
        "skill"].__class__ != list or rq["hashtag"].__class__ != list or rq["content"].__class__ != list or rq[
        "interests"].__class__ != list or rq["find_job"].__class__ != bool:
        abort(400)
    hashtag = check_list_hashtag(rq["hashtag"])
    if check_place(rq["place"]) == "":
        abort(400, 'Error 400: Place not exist')
    if len(hashtag) == 0:
        abort(400, 'Error 400: Hashtag not exist')
    if not check_skill(rq["skill"]):
        abort(400, 'Error 400: Skill is not in the correct format')
    if not check_content(rq["content"]):
        abort(400, 'Error 400: Content is not in the correct format')
    for interest in rq["interests"]:
        if interest.__class__ != str:
            abort(400)
    try:
        dob = datetime.datetime.strptime(rq["dob"], '%d/%m/%Y')
    except:
        abort(400, 'Error 400: Day of birth is not in the correct format')

    try:
        update_cv(ObjectId(id), db_cv, rq["name"], rq["gender"], rq["avatar"], rq["position"], dob, rq["address"], rq["email"], rq["phone"], rq["place"], rq["skill"], hashtag, rq["content"], rq["interests"], rq["find_job"])
    except:
        abort(403)

    return "ok"


@bp.route('/cv/<id>', methods=['DELETE'])
@token_auth.login_required()
def delete_cv(id):
    global db_cv
    token = g.current_token
    try:
        db_cv = find_cv(ObjectId(id), {"_id": 0, "applicant": 1})
    except:
        abort(403)

    if db_cv is None:
        abort(404)

    if db_cv["applicant"] != token.id_user:
        abort(405)

    try:
        delete_cv(ObjectId(id))
    except:
        abort(403)
    return "ok"


@bp.route("/cv/my", methods=['GET'])
@token_auth.login_required(role="applicant")
def get_my_list_cv():
    global page
    try:
        page = int(request.args.get('page', default=0))
    except:
        abort(400)
    token = g.current_token
    try:
        list_cv = get_list_cv_by_id_applicant(token.id_user, page)
        return {"list_cv": list_cv}
    except:
        abort(403)
