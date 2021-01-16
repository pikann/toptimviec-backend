from flask import Blueprint, Flask

bp = Blueprint('api', __name__)

@bp.route('/')
def index():
     return "Back-end for toptimviec"