from flask import Blueprint, Flask

bp = Blueprint('api', __name__)

from app import routes