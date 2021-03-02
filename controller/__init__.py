from flask import Blueprint, Flask
from pymongo import MongoClient
import yagmail

bp = Blueprint('api', __name__)
client = MongoClient('mongodb+srv://pikann22:Wt7GsHbs7LmFWVT7@toptimviec.4zz7i.mongodb.net/test')
db = client.toptimviec
yag = yagmail.SMTP(user='toptimviec@gmail.com', password='TopTimViec1')
list_hashtag = [d["name"] for d in list(db.hashtag.find({}, {"_id": 0, "name": 1}))]
list_place = [p["name"] for p in list(db.place.find({}, {"_id": 0, "name": 1}))]
# email_form = open("email_form.html", "r").read().replace("\n", " ")

# from controller.applicant import *
# from controller.employer import *
# from controller.validate import *
# from controller.login import *
# from controller.forget_password import *
# from controller.post import *
# from controller.global_data import *

@bp.route('/')
def index():
     return "Back-end for toptimviec"