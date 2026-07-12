import smtplib
import json
import os
from email.mime.text import MIMEText

script_dir = os.path.dirname(os.path.abspath(__file__))
passwrd = os.getenv("appPass")

with open(os.path.join(script_dir, "available.json"), "r") as readFile:
    data = "\n".join(json.load(readFile))

print(data)

def sendEmail(sender, recipients, subject, text):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtpServ:
        smtpServ.login(sender, passwrd)
        smtpServ.sendmail(sender, recipients, str(msg))

sendEmail("realdynedl@gmail.com", ["realdynedl@gmail.com"], "available", data)