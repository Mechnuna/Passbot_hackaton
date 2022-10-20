from crypt import methods
from ctypes import pointer
import os
import plistlib
import sys

htc_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('/../')
if htc_path not in sys.path:
    sys.path.append(htc_path)
from ops.manager import Manager
from db.base import ENGINE
from forms import UserForm
from forms import AuthForm
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS


#DB
from ops.manager import Manager
from crud.authorized_users import AuthorizedUserCRUD
from crud.auth_tickets import AuthTicketsCRUD
from crud.entry_request import EntryRequestCRUD
from db.base import ENGINE
from models.entry_request import EntryRequestBaseModel 
from models.authorized_users import AuthorizedUsersBaseModel
from models.auth_tickets import AuthTicketsBaseModel
from datetime import date
from models.enums import Campuses, Roles
#DB

app = Flask(__name__)
cors = CORS(app)
manager = Manager(ENGINE)
app.config['SECRET_KEY'] = 'ac623111b8c5d81eb4efbd3a8bc673a9f7408fe0750bee5f'

@app.route("/receiver", methods=["POST"])
def	postME():
	data = request.get_json()
	data = jsonify(data)
	print(data.json)
	return data


@app.route("/application/<id_usr>")
def show_application(id_usr):
	try:
		data = manager.select_from_entry_request_by_tg(id_usr)
		return render_template('applic.html',data=data,id=id_usr)
	except Exception as e:
		print(e)
		return "Что-то пошло не так"


@app.route('/user/<id_usr>', methods=('GET', 'POST'))
def user(id_usr):
	if request.method == 'POST':
		try:
			us = manager.select_auth_user_by_tg(id_usr);
			er_model = EntryRequestBaseModel(
				TG_NAME=id_usr,
				INITIATOR_NAME=request.form['user_name'],
				RESPONSIBLE_NAME=request.form['user_name'],
				GUEST_NAME=request.form['guest_name'],
				CAMPUS=us.CAMPUS,
				BOOKING_DATE=request.form['date']
			)
	
			manager.create_new_entry_request(er_model=er_model)
			return render_template('fine.html', id=id_usr)
		except Exception as e:
			print(e)
			return "Invalid format"
	else:
		print(id_usr)
		if manager.select_auth_user_by_tg(tg_name=id_usr):
			if manager.check_if_entry_request_creatable(id_usr,Roles.LEARNER.value).CAN_CREATE:
				return render_template('index.html',id=id_usr)
			return render_template('error.html',id=id_usr)
		else:
			return "Авторизуйся сначала!"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
