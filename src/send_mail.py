from http import server
import os
import smtplib
import random 
from auth.config import password

def send_mail(mail):
	sender = "passbot21school@gmail.com"
	sever = smtplib.SMTP("smtp.gmail.com", 587)
	sever.starttls()
	code = ""
	for i in range(6):
		code += str(random.randint(0,10))
	message = f"Subject: PassBot Code\n\nYour code: {code}"
	sever.login(sender, password)
	sever.sendmail(sender, mail, message)
	return code
