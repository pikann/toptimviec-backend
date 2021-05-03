from pymongo import MongoClient
import smtplib

client = MongoClient('mongodb+srv://pikann22:Wt7GsHbs7LmFWVT7@toptimviec.4zz7i.mongodb.net/test')
db = client.toptimviec
smtp = smtplib.SMTP('smtp.gmail.com:587')
smtp.starttls()
smtp.login('toptimviec@gmail.com', 'TopTimViec1')
email_form = open("templates/email_form.html", "r").read().replace("\n", " ")