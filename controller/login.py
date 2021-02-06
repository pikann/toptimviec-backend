from flask import g, abort
from controller import bp, db
from controller.auth import basic_auth, token_auth


@bp.route('/login', methods=['POST'])
@basic_auth.login_required
def login():
    token = g.current_token.get_token()
    try:
        user = db.user.find_one({"_id": token.id_user}, {"_id": 0, "role": 1})
        if user["role"] == "applicant":
            applicant = db.applicant.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"token": token.show_token(), "id_user": str(token.id_user), "role": user["role"],
                    "name": applicant["name"], "avatar": applicant["avatar"]}
        if user["role"] == "employer":
            employer = db.employer.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"token": token.show_token(), "id_user": str(token.id_user), "role": user["role"],
                    "name": employer["name"], "avatar": employer["avatar"]}
        abort(403)
    except:
        abort(403)


@bp.route('/logout', methods=['DELETE'])
@token_auth.login_required
def logout():
    token = g.current_token.get_token()
    if token.revoke_token() == "ok":
        return "ok"
    else:
        abort(403)


@bp.route('/info', methods=['GET'])
@token_auth.login_required
def info():
    token = g.current_token.get_token()
    try:
        user = db.user.find_one({"_id": token.id_user}, {"_id": 0, "role": 1})
        if user["role"] == "applicant":
            applicant = db.applicant.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"id_user": str(token.id_user), "role": user["role"],
                    "name": applicant["name"], "avatar": applicant["avatar"]}
        if user["role"] == "employer":
            employer = db.employer.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"id_user": str(token.id_user), "role": user["role"],
                    "name": employer["name"], "avatar": employer["avatar"]}
        abort(401)
    except:
        abort(403)
