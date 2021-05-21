from flask import abort
from routes import bp
from services.auth import token_auth
from services.admin import count_user, count_cv, count_post, count_post_unexpired, count_employer, count_applicant


@bp.route('/general-info', methods=['GET'])
@token_auth.login_required(role="admin")
def get_general_infomation():
    try:
        rs = {
            "count_user": count_user(),
            "count_cv": count_cv(),
            "count_post": count_post(),
            "count_post_unexpired": count_post_unexpired(),
            "count_employer": count_employer(),
            "count_applicant": count_applicant()
        }
    except:
        abort(403)

    return rs
