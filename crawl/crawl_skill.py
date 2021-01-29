import requests
from bs4 import BeautifulSoup
from controller import db

req=requests.get("https://itviec.com/jobs-skill-index")
soup=BeautifulSoup(req.text, "html.parser")

list_skill=soup.find("ul", {"class": "skill-tag__list"}).find_all("a")

for skill in list_skill:
    print(skill.text.strip())
    db.hashtag.insert_one({"name": skill.text.strip()})

db.hashtag.insert_one({"name": "Intern"})
db.hashtag.insert_one({"name": "Junior"})
db.hashtag.insert_one({"name": "Senior"})