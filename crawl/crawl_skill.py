import requests
from bs4 import BeautifulSoup
from controller import db

req=requests.get("https://itviec.com/jobs-skill-index")
soup=BeautifulSoup(req.text, "html.parser")

list_skill=soup.find("ul", {"class": "skill-tag__list"}).find_all("a")

for skill in list_skill:
    print(skill.text.strip())
    db.hashtag.update_one({"name": skill.text.strip()}, {"$set": {"name": skill.text.strip()}}, upsert=True)

db.hashtag.update_one({"name": "Intern"}, {"$set": {"name": "Intern"}}, upsert=True)
db.hashtag.update_one({"name": "Fresher"}, {"$set": {"name": "Fresher"}}, upsert=True)
db.hashtag.update_one({"name": "Junior"}, {"$set": {"name": "Junior"}}, upsert=True)
db.hashtag.update_one({"name": "Senior"}, {"$set": {"name": "Senior"}}, upsert=True)