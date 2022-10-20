import smtplib
from auth.config import password
from keyring import get_keyring
get_keyring()

class	Message:
	def	__init__(self, *args):
		self.content = ""
		for x in args:
			self.content += str(x)

class	Sender:
	def	__init__(self, name, mail):
		self.name = name
		self.mail = mail
	def	sendMail(self, recipient, message : Message) :
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.starttls()
		server.login(self.mail, password)
		server.sendmail(self.mail, recipient, message.content)
