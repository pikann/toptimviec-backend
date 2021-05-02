from flask import g, abort, request
from routes import bp
from services.auth import token_auth
from services.applicant import get_applicant_by_id, update_applicant_profile, update_applicant_avatar
from services.employer import get_employer_by_id, update_employer_profile, update_employer_avatar
from services.global_data import check_place
from services.user import reset_password


@bp.route('/info', methods=['GET'])
@token_auth.login_required
def info():
    token = g.current_token
    try:
        if token.role == "applicant":
            applicant = get_applicant_by_id(token.id_user, {"_id": 0, "name": 1, "avatar": 1})
            return {"id_user": str(token.id_user), "role": token.role,
                    "name": applicant["name"], "avatar": applicant["avatar"]}
        if token.role == "employer":
            employer = get_employer_by_id(token.id_user, {"_id": 0, "name": 1, "avatar": 1})
            return {"id_user": str(token.id_user), "role": token.role,
                    "name": employer["name"], "avatar": employer["avatar"]}
        abort(401)
    except:
        abort(403)


@bp.route('/profile', methods=['GET'])
@token_auth.login_required
def get_profile():
    token = g.current_token
    try:
        if token.role == "applicant":
            applicant = get_applicant_by_id(token.id_user,
                                            {"_id": 0, "name": 1, "avatar": 1, "gender": 1, "dob": 1, "place": 1})
            return applicant
        if token.role == "employer":
            employer = get_employer_by_id(token.id_user, {"_id": 0, "name": 1, "avatar": 1, "bio": 1})
            return employer
        abort(401)
    except:
        abort(403)


@bp.route('/profile', methods=['PUT'])
@token_auth.login_required
def put_profile():
    token = g.current_token
    rq = request.json

    if token.role == "applicant":
        if not rq or not 'name' in rq or not 'gender' in rq or not 'dob' in rq or not 'place' in rq:
            abort(400)

        if rq["name"].__class__ != str or rq["gender"].__class__ != bool or rq["dob"].__class__ != str or rq["place"].__class__ != str:
            abort(400)

        try:
            place = check_place(rq["place"])
        except:
            abort(400)

        try:
            update_applicant_profile(token.id_user, rq["name"], rq["gender"], rq["dob"], place)
        except:
            abort(403)
    elif token.role == "employer":
        if not rq or not 'name' in rq or not 'bio' in rq:
            abort(400)

        if rq["name"].__class__ != str or rq["bio"].__class__ != str:
            abort(400)

        try:
            update_employer_profile(token.id_user, rq["name"], rq["bio"])
        except:
            abort(403)

    return "ok"


@bp.route('/avatar', methods=['PUT'])
@token_auth.login_required
def put_avatar():
    token = g.current_token
    rq = request.json

    if not rq or not 'avatar' in rq:
        abort(400)

    if rq["avatar"].__class__ != str:
        abort(400)

    try:
        if token.role == "applicant":
            update_applicant_avatar(token.id_user, rq["avatar"])
        elif token.role == "employer":
            update_employer_avatar(token.id_user, rq["avatar"])
    except:
        abort(403)

    return "ok"


@bp.route('/reset-password', methods=['PUT'])
@token_auth.login_required
def reset_password_route():
    global rs
    token = g.current_token
    rq = request.json

    if not rq or not 'old_password' in rq or not 'new_password' in rq:
        abort(400)

    try:
        rs = reset_password(token.id_user, rq["old_password"], rq["new_password"])
    except:
        abort(403)

    if rs > 0:
        return "ok"
    else:
        abort(412)
