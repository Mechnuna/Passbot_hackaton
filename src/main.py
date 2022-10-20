import json
import random
import re
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, WebAppInfo
from auth.config import token,adm_toke
from apilib.intra import IntraAPIClient
from auth.auth import Authentificator
from send_mail import send_mail
from valid_form import parse_date, parse_name


############### DB ################
from re import T
from fastapi import FastAPI

from config import web_app_url
from ops.manager import Manager
from crud.authorized_users import AuthorizedUserCRUD
from crud.auth_tickets import AuthTicketsCRUD
from db.base import ENGINE
from models.entry_request import EntryRequestBaseModel
from models.authorized_users import AuthorizedUsersBaseModel
from models.auth_tickets import AuthTicketsBaseModel
from datetime import date
from models.enums import Campuses, Roles
manager = Manager(ENGINE)
############### DB ################

bot = telebot.TeleBot(token)
ic = IntraAPIClient()
au = Authentificator()


def webAppKeyboard(m): #создание клавиатуры с webapp кнопкой
	keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	webAppTest = WebAppInfo(f"{web_app_url}/user/{m.from_user.username}")
	print("Open")
	one_butt = KeyboardButton(text="Открыть веб форму", web_app=webAppTest)
	keyboard.add(one_butt)
	return keyboard

#Ловим все колл-беки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	req = call.data.split()
	if not req:
		return
	if req[0] == 'guest':
		print(call.from_user.username)
		bot.send_message(call.from_user.id, "Введите свой город:\nMoscow, KZN,NSK?\n")
		bot.register_next_step_handler(call.message, make_guest)
		# creatable = manager.check_if_entry_request_creatable(call.from_user.username, 'OUTSIDER')
		# if (not creatable.CAN_CREATE):
		# 	bot.send_message(call.from_user.id, "Невозможно создать форму")
		# 	bot.send_message(call.from_user.id, creatable.MESSAGE)
		# else:
		# 	bot.send_message(call.from_user.id, "Заполните заявку:\nВведите ФИО гостя:\nВведите дату посещения:\n")
		# 	bot.register_next_step_handler(call.message, make_request_guest)
	if req[0] == 'user':
		find_user(call.message)
	if req[0] == 'msk':
		bot.send_message(call.from_user.id, "Введите свой ник")
		bot.register_next_step_handler(call.message, intra_user)
	if req[0] == 'kzn' or req[0] == 'nvs':
		bot.send_message(call.from_user.id, "Введите свой ник")
		bot.register_next_step_handler(call.message, sber_user, "KZN")
	if req[0] == 'back':
		find_user(call.message)
	if req[0] == 'try_again':
		bot.register_next_step_handler(call.message, auth, call.mes)
	if req[0] == 'try_again':
		bot.register_next_step_handler(call.message, sber_user)
	if req[0] == "make_request":
		creatable = manager.check_if_entry_request_creatable(call.from_user.username, "LEARNER")
		if (not creatable.CAN_CREATE):
			bot.send_message(call.from_user.id, "Невозможно создать форму")
			bot.send_message(call.from_user.id, creatable.MESSAGE)
		else:
			bot.send_message(call.from_user.id, "Заполните заявку:\nВведите ваше ФИО:\nВведите ФИО гостя:\nВведите дату посещения:\n")
			bot.register_next_step_handler(call.message, make_request)
	if req[0] == "make_request_guest":
		bot.send_message(call.from_user.id, "Заполните заявку:\nВведите ваше ФИО:\nВведите дату посещения:\n")
		bot.register_next_step_handler(call.message, make_request_guest)
	if req[0] == "see_my_app":
		show_application(call.message, call.from_user.username)
	if req[0] == "adm_app":
		all_tik = manager.select_entry_request_status_new()
		adm_watch_ticket(call.message,all_tik)
	if req[0] == "adm_make":
		creatable = manager.check_if_entry_request_creatable(call.from_user.username, "LEARNER")
		bot.send_message(call.from_user.id, "Заполните заявку:\nВведите ваше ФИО\nВведите ФИО гостя:\nВведите дату посещения:\n")
		bot.register_next_step_handler(call.message, make_request, "ADM")

	if 'pagination' in req[0]:
      	#Расспарсим полученный JSON
		all_tik = manager.select_entry_request_status_new()
		json_string = json.loads(req[0])
		count = json_string['CountPage']
		page = json_string['NumberPage']
				#Пересоздаем markup
		markup = InlineKeyboardMarkup()
		markup.add(InlineKeyboardButton(text='Изменить', callback_data='adm_edit_ticket'))
        #markup для первой страницы
		if page == 0:
			markup.add(InlineKeyboardButton(text=f'{page+1}/{count}', callback_data=f'no'),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        #markup для второй страницы
		elif page+1 == count:
			markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page+1}/{count}', callback_data=f'no'))
        #markup для остальных страниц
		else:
			markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + "}"),
                           InlineKeyboardButton(text=f'{page+1}/{count}', callback_data=f'no'),
                           InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page+1) + ",\"CountPage\":" + str(count) + "}"))
		print(page)
		print(str(all_tik[0]))
		s = const_message(all_tik[page])
		bot.edit_message_text(s, reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)

def make_guest(m):
	if m.text != 'Moscow' and m.text != 'NSK' and m.text != 'KZN':
		markup = InlineKeyboardMarkup()
		markup.add(
			InlineKeyboardButton(text=f'Попробовать снова', callback_data="guest"))
		bot.send_message(m.chat.id, f"Неправильный город, попробуй еще раз\n Что дальше?", reply_markup=markup)
	else:
		manager.create_new_auth_user(auth_user_model=AuthorizedUsersBaseModel(
					RESPONSIBLE_NICK=m.from_user.username,
					TG_NAME=m.from_user.username,
					CAMPUS=m.text,
					INITIATOR_NAME=m.from_user.username,
					ROLE="OUTSIDER"
				))
		bot.send_message(m.from_user.id, "Заполните заявку:\nВведите свое ФИО:\nВведите дату посещения:\n")
		bot.register_next_step_handler(m, make_request_guest)


#сообщение для админки
def const_message(all_tik):
	s = f"ID Заявки {all_tik.ID}\n\
		\nTelegram пользователя:\n\
		{all_tik.TG_NAME}\nИмя отправителя:\n\
		{all_tik.RESPONSIBLE_NAME}\nНик отправителя:\n\
		{all_tik.RESPONSIBLE_NICK}\nКампус:\n\
		{all_tik.CAMPUS}\nИмя гостя:\n\
		{all_tik.GUEST_NAME}\n\nДата посещения:\n\
		{all_tik.BOOKING_DATE}\n\nСтатус: "
	if all_tik.STATUS == 'new':
		s += "ждет одобрения⌛\n"
	else:
		s += "одобрено✅"
	return s


def adm_panel(m):
	markup = InlineKeyboardMarkup()
	markup.add(
			   InlineKeyboardButton(text=f'Посмотреть заявки', callback_data="adm_app"),
			   InlineKeyboardButton(text=f'Создать заявку', callback_data="adm_make"),
	)

	bot.send_message(m.chat.id, "Доступные функции:", reply_markup=markup)


def adm_watch_ticket(m,all):
    count = len(all) - 1
    page = 0
    print(count)
    s = const_message(all[0])
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Изменить', callback_data='adm_edit_ticket'))
    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f'no'),
               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(0) + ",\"CountPage\":" + str(count) + "}"))
    bot.send_message(m.chat.id, s, reply_markup = markup)


def adm_token(m):
	if m.text == adm_toke:
		adm_panel(m)
	else:
		print(m.text, adm_toke)

#Выбор кампуса
def auth(m):
	print(manager.select_auth_ticket_by_name(m.from_user.username))
	try:
		if (manager.select_auth_ticket_by_name(m.from_user.username).TICKET == m.text) :
			manager.update_auth_ticket_status(m.from_user.username, "confirmed")
			auth_user = manager.select_auth_ticket_by_name(m.from_user.username)
			manager.create_new_auth_user(auth_user_model=AuthorizedUsersBaseModel(
				RESPONSIBLE_NICK=auth_user.RESPONSIBLE_NICK,
				TG_NAME=auth_user.TG_NAME,
				CAMPUS=auth_user.CAMPUS,
				INITIATOR_NAME=auth_user.INITIATOR_NAME,
				ROLE="LEARNER"
			))
			show_button(m)
			print("lol")
		else:
			markup = InlineKeyboardMarkup()
			markup.add(InlineKeyboardButton(text='Назад', callback_data='back'),
					InlineKeyboardButton(text=f'Ввести другой код', callback_data="retry_code") )
			bot.send_message(m.chat.id, "Неверный код", reply_markup=markup)
	except Exception as e:
		pass
		print(e)

# Вход со сбера - атоматической проверки нет
def sber_user(m, campus):
	valid_token = send_mail(f"{m.text.lower()}@student.21-school.ru")
	bot.send_message(m.chat.id, f" 👋 Добро пожаловать, {m.text}\nКод доступа отправлен тебе на почту {m.text}@student.21-school.ru,")
	manager.create_new_auth_ticket_if_not_exists(auth_model=AuthTicketsBaseModel(
		TG_NAME=f"{m.from_user.username}",
		TICKET=valid_token,
		RESPONSIBLE_NICK=m.text.lower(),
		CAMPUS=campus,
		INITIATOR_NAME=m.text.lower()
	))
	bot.register_next_step_handler(m, auth)


#Вход для юзеров с интры - автоматическа проверка на валидность ника
def intra_user(m):
	try:
		nik = m.text.lower()
		id_m = send_mail(m.from_user.username, "Подожди минутку, идет проверка...")
		usr = ic.get(f"users/{nik}")
		bot.delete_message(id_m.message_id)
		valid_token = send_mail(usr.json()['email'])
		bot.send_message(m.chat.id, f"👋 Добро пожаловать, {usr.json()['displayname']}\nКод доступа отправлен тебе на почту {usr.json()['email']}")
		manager.create_new_auth_ticket_if_not_exists(auth_model=AuthTicketsBaseModel(
			TG_NAME=f"{m.from_user.username}",
			TICKET=valid_token,
			RESPONSIBLE_NICK=m.text.lower(),
			CAMPUS=usr.json()['campus'][0]['name'],
			INITIATOR_NAME=m.text.lower()
		))
		bot.register_next_step_handler(m, auth)
	except Exception as e:
		markup = InlineKeyboardMarkup()
		markup.add(InlineKeyboardButton(text='Назад', callback_data='back'),
				InlineKeyboardButton(text=f'Ввести другой ник', callback_data="retry_nick_intra") )
		bot.send_message(m.chat.id, "Неверный ник( Попытайся еще раз", reply_markup=markup)


#Показать кнопошки
def show_button(m):
	markup =  InlineKeyboardMarkup()
	button1 = InlineKeyboardButton(text = "Создать заявку", callback_data="make_request")
	button2 = InlineKeyboardButton(text = "Мои Заявки",callback_data="see_my_app")
	markup.add(button1, button2)
	bot.send_message(m.chat.id, text="Авторизован!", reply_markup=markup)


def show_button_guest(m):
	markup =  InlineKeyboardMarkup()
	button1 = InlineKeyboardButton(text = "Создать заявку", callback_data="make_request_guest")
	button2 = InlineKeyboardButton(text = "Мои Заявки",callback_data="see_my_app")
	markup.add(button1, button2)
	bot.send_message(m.chat.id, text="Авторизован!", reply_markup=markup)


def show_application(m, username):
	message = ""
	message += "Ваши заявки:\n"
	entries = manager.select_entry_request_by_tg_name(username)
	if (entries is None):
		message += "Нет заявок"
	else:
		for entry in entries:
			message += f"ID Заявки: {entry.ID}\n"
			message += f"Имя гостя:\n{entry.GUEST_NAME}\nСтатус: "
			if entry.STATUS == 'new':
				message += "ждет одобрения⌛\n"
			else:
				message += "одобрено✅"
			message += f"{entry.STATUS}\n"
			message += '\n'
	bot.send_message(m.chat.id, message)
	#Добавить запрос к БД и вывод информации

def	invalid_form(m, reason, adm=False):
	markup = InlineKeyboardMarkup()
	if adm:
		markup.add(InlineKeyboardButton(text='Назад', callback_data='back'),
			InlineKeyboardButton(text=f'Попробовать снова', callback_data="adm_make") )
	else:
		markup.add(InlineKeyboardButton(text='Назад', callback_data='back'),
				InlineKeyboardButton(text=f'Попробовать снова', callback_data="make_request") )
	bot.send_message(m.chat.id, f"Форма не принята.Причина: {reason}\n Что дальше?", reply_markup=markup)

#Заполнить формочку
def make_request(m, adm=False):
	message = m.text.splitlines()
	if (len(message)!= 3):
		invalid_form(m, "Форма заполнена неверно", adm)
		return
	try:
		entry_data = EntryRequestBaseModel(
			TG_NAME=m.from_user.username,
			INITIATOR_NAME=parse_name(message[0]),
			GUEST_NAME=parse_name(message[1]),
			BOOKING_DATE=parse_date(message[2])
		)
	except Exception as e:
		invalid_form(m, str(e), adm)
		return
	manager.create_entry_request_using_role(m.from_user.username, entry_data)
	bot.send_message(m.chat.id, "Заявка принята")
	show_button(m)
	return

#Заполнить формочку
def make_request_guest(m):
	message = m.text.splitlines()
	if (len(message) != 2):
		invalid_form(m, "Форма заполнена неверно")
		return
	else:
		try:
			entry_data = EntryRequestBaseModel(
				TG_NAME=m.from_user.username,
				GUEST_NAME=parse_name(message[0]),
				INITIATOR_NAME=parse_name(message[0]),
				BOOKING_DATE=parse_date(message[1])
			)
		except Exception as e:
			invalid_form(m, str(e))
			return
		manager.create_entry_request_using_role(m.from_user.username, entry_data)
		bot.send_message(m.chat.id, "Заявка принята.")
		show_button_guest(m)
		return
	# bot.register_next_step_handler(m, push_data)

def find_user(m):
	markup = InlineKeyboardMarkup()
	markup.add(
			   InlineKeyboardButton(text=f'Казань', callback_data="kzn"),
			   InlineKeyboardButton(text=f'Новосибирск', callback_data="nvs"),
			   InlineKeyboardButton(text='Москва', callback_data='msk')
	)

	bot.send_message(m.chat.id, "Теперь выбери свой кампус", reply_markup=markup)


# def auth(m, valid_token):
# 	try:
# 		# Сюда вставить отправку сообщения
# 		if m.text == valid_token:
# 			show_button(m)
# 		else:
# 			print(m.text,valid_token)
# 			bot.send_message(m.chat.id, "No valid")
# 			markup = InlineKeyboardMarkup()
# 			print(manager.select_auth_ticket_by_name(m.from_user.username))
# 			markup.add(InlineKeyboardButton(text='Назад', callback_data='back'),
# 					InlineKeyboardButton(text=f'Ввести другой код', callback_data="try_again"),
# 					InlineKeyboardButton(text=f'Отправить еще раз', callback_data="resend_mail"), )
# 			bot.register_next_step_handler(m, auth, valid_token)
# 	except Exception as e:
# 		print(e)


#Показать кнопошки
def show_button(m):
	usr = manager.select_auth_user_by_tg(m.chat.username)
	bot.send_message(m.chat.id, text=f"Меню пользователя: {usr.RESPONSIBLE_NICK}", reply_markup=webAppKeyboard(m))
	markup =  InlineKeyboardMarkup()
	button1 = InlineKeyboardButton(text = "Создать заявку", callback_data="make_request")
	button2 = InlineKeyboardButton(text = "Мои Заявки",callback_data="see_my_app")
	markup.add(button1, button2)
	button3 = InlineKeyboardButton(text = "Изменить заявку",callback_data="edit_app")
	markup.add(button3)
	bot.send_message(m.chat.id, text="Чего хочешь сделать?", reply_markup=markup)




#Функция для отправки заявки а базу данных
def push_data(*argc):
	pass

#Начало диалога
@bot.message_handler(commands=['start'])
def start_message(m):
	if (manager.select_auth_user_by_tg(m.from_user.username) is None):
		start_buttons(m)
	else:
		show_button(m)

def	start_buttons(m):
	markup = InlineKeyboardMarkup()
	markup.add(InlineKeyboardButton(text='Я гость', callback_data='guest'),
			InlineKeyboardButton(text=f'Я ученик', callback_data="user"))
	bot.send_message( m.chat.id, 'Привет, я бот для проверки телеграмм webapps!)', reply_markup=markup)


@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webAppMes):
   print(webAppMes) #вся информация о сообщении
   print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота
   bot.send_message(webAppMes.chat.id, f"получили инофрмацию из веб-приложения: {webAppMes.web_app_data.data}") 


@bot.message_handler(commands=['adm'])
def adm(m):
	bot.send_message( m.chat.id, 'Введите секретный токен')
	bot.register_next_step_handler(m, adm_token)


@bot.message_handler(commands=['exit'])
def exit(m):
	bot.send_message(m.chat.id, 'Ты точно хочешь выйти? [Y/n]')
	bot.register_next_step_handler(m, delete)


def delete(m):
	if m.text.lower() == 'y':
		pass

if __name__ == '__main__':
	bot.polling(none_stop=True)