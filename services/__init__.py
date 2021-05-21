from pymongo import MongoClient

client = MongoClient('mongodb+srv://pikann22:Wt7GsHbs7LmFWVT7@toptimviec.4zz7i.mongodb.net/test')
db = client.toptimviec
email_form = open("templates/email_form.html", "r").read().replace("\n", " ")