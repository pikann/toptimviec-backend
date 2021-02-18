from jinja2 import Template
from controller import yag

form = open("email_form.html", "r").read().replace("\n", " ")
mail_content=Template(form).render({"content": "abc", "href": "#", "button_text": "Xác nhận tài khoản"})
print(mail_content)

yag.send(to="hvhai22@gmail.com", subject="Test", contents=mail_content)