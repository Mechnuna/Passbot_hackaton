from auth.sender import Sender, Message
import vcode

class	Authentificator:
	def	__init__(self):
		self.sender = Sender("PassBot", "passbot21school@gmail.com")
	def	sendCode(self, mail) -> str :
		code = vcode.digits()
		message = Message("Enter code " + code + " to telegram chat")
		self.sender.sendMail(mail, message)
		return (code)
