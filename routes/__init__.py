from flask import Blueprint, Flask, render_template

bp = Blueprint('api', __name__)

from routes.applicant import *
from routes.employer import *
from routes.validate import *
from routes.login import *
from routes.forget_password import *
from routes.post import *
from routes.global_data import *
from routes.cv import *
from routes.list_candidate import *
from routes.mail import *
from routes.notification import *


@bp.route('/')
def index():
     return "Back-end for toptimviec"


@bp.route('/test-socket')
def test_socket():
    return render_template("test.html")