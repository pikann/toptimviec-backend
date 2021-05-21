import smtplib

smtp_host = 'smtp.office365.com:587'
smtp_user = 'toptimviec@gmail.com'
smtp_password = 'TimviecTop123'


def send_email(email, msg):
    smtp = smtplib.SMTP(smtp_host)
    smtp.starttls()
    smtp.login(smtp_user, smtp_password)

    smtp.sendmail('toptimviec@gmail.com', email, msg.as_string())