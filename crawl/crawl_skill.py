from selenium import webdriver
from selenium.webdriver.common.by import By
from controller import db

driver = webdriver.Chrome(r"C:\Users\hvhai\Downloads\chromedriver_win32\chromedriver.exe")
driver.get("https://itviec.com/jobs-skill-index")
list_skill=driver.find_element(By.XPATH, ".//ul[@class='skill-tag__list']").find_elements_by_tag_name("a")

for skill in list_skill:
    print(skill.text.strip())
    db.hashtag.insert_one({"name": skill.text.strip()})

db.hashtag.insert_one({"name": "Intern"})
db.hashtag.insert_one({"name": "Junior"})
db.hashtag.insert_one({"name": "Senior"})