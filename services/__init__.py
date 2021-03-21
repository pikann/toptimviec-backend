from pymongo import MongoClient
import yagmail

client = MongoClient('mongodb+srv://pikann22:Wt7GsHbs7LmFWVT7@toptimviec.4zz7i.mongodb.net/test')
db = client.toptimviec
yag = yagmail.SMTP(user='toptimviec@gmail.com', password='TopTimViec1')
email_form = open("email_form.html", "r").read().replace("\n", " ")