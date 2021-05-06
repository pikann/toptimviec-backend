from flask import abort
from routes import bp
from services.auth import token_auth
from services.cloudinary_signature import get_signature


@bp.route('/cloudinary', methods=['GET'])
@token_auth.login_required()
def get_cloudinary_signature():
    try:
        return get_signature()
    except:
        abort(403)
