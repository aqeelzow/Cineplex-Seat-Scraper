import smtplib
import json
import os
from email.mime.text import MIMEText
from datetime import datetime
import schedule
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
passwrd = os.getenv("appPass")
with open(os.path.join(script_dir, "available.json"), "r") as readFile:
    data = json.load(readFile)
timestamps = "\n\nProcessed at: " + data[2] + "\nSent at: " + datetime.now().strftime("%H:%M:%S")
if type(data[1]) == list:
    showtimeList = "\n".join(data[1]) + timestamps
else:
    showtimeList = (data[1]) + timestamps
showtimeSubject = data[0]
print(data)

def sendEmail(sender, recipients, subject, text):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtpServ:
        smtpServ.login(sender, passwrd)
        smtpServ.sendmail(sender, recipients, str(msg))

sendEmail("realdynedl@gmail.com", ["realdynedl@gmail.com"], showtimeSubject, showtimeList)