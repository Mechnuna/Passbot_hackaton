from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (StringField)
from wtforms.validators import InputRequired, Length

class	UserForm(FlaskForm):
	nick = StringField('Ник на платформе', validators=[InputRequired()])
	# mail = StringField('Почта учебной платформы', validators=[InputRequired()])

class	AuthForm(FlaskForm):
	code = StringField('Код из почты.', validators=[InputRequired(), Length(6)])