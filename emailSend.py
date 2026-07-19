import smtplib
import json
import os
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import schedule
import time

def readInfo(emailKey, dictNum):
    showtime = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #passwrd = os.getenv("appPass")
    with open(os.path.join(script_dir, "available.json"), "r") as readFile:
        data = json.load(readFile)
    timestamps = "\n\nProcessed at: " + data[emailKey][dictNum][2] + "\nSent at: " + datetime.now().strftime("%H:%M:%S")
    if type(data[emailKey][dictNum][1]) == list:
        showtime.append("\n".join(data[emailKey][dictNum][1]) + timestamps)
    else:
        showtime.append((data[emailKey][dictNum][1]) + timestamps)
    showtime.append(data[emailKey][dictNum][0])
    print(data[emailKey][dictNum])
    return showtime


def sendEmail(sender, recipients, subject, text, password):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtpServ:
        smtpServ.login(sender, password)
        smtpServ.sendmail(sender, recipients, str(msg))
load_dotenv()
info = readInfo()