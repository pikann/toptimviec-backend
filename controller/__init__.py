from flask import Blueprint, Flask
from pymongo import MongoClient

bp = Blueprint('api', __name__)
client = MongoClient('mongodb+srv://pikann22:Wt7GsHbs7LmFWVT7@toptimviec.4zz7i.mongodb.net/test')
db = client.toptimviec

@bp.route('/')
def index():
     return "Back-end for toptimviec"