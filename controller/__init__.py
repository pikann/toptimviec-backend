from flask import Blueprint, Flask
from pymongo import MongoClient
import yagmail

bp = Blueprint('api', __name__)
client = MongoClient('mongodb+srv://pikann22:Wt7GsHbs7LmFWVT7@toptimviec.4zz7i.mongodb.net/test')
db = client.toptimviec
yag = yagmail.SMTP(user='toptimviec@gmail.com', password='TopTimViec1')

from controller.applicant import *
from controller.employer import *
from controller.validate import *
from controller.login import *

@bp.route('/')
def index():
     return "Back-end for toptimviec"