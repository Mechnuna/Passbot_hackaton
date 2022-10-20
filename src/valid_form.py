from datetime import datetime
from dateutil.parser import parse

def	parse_date(date : str) -> datetime:
	try:
		date = parse(date).date()
		current_date = date.today()
	except Exception:
		raise Exception("Неверный формат даты")
	else:
		if (date <= current_date):
			print(date)
			print(current_date)
			raise Exception("Введенная дата уже в прошлом")
		return (current_date)

def	parse_name(name : str) -> str:
	valid = name != '' and all(chr.isalpha() or chr.isspace() for chr in name)
	if (not valid):
		print(name)
		raise Exception("Недопустимые символы в ФИО")
	else:
		split_name = name.split(' ')
		res_str = " ".join(split_name)
		return res_str

if __name__ == '__main__':
	print(parse_date("string"))