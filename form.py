from models import User
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,TextAreaField
from wtforms.validators import InputRequired,email,equal_to,length,ValidationError
from flask import flash



class RegisterForm(FlaskForm):
    username = StringField('username',validators=[InputRequired()])
    email = StringField('email',validators=[InputRequired(),email()])
    password = PasswordField('password',validators=[InputRequired(),length(min=4)])
    password2 =PasswordField('confirm password',validators=[InputRequired(),equal_to('password',message='password doesnt much')])


    def validate_username(form,field):
        if User.select().where(User.username == field.data):
            raise ValidationError('username already exist')
    
    def validate_email(form,field):
        if User.select().where(User.email == field.data):
            raise ValidationError('email already exist')


class LoginForm(FlaskForm):
    email = email = StringField('email',validators=[InputRequired(),email()])
    password = PasswordField('password',validators=[InputRequired()])


class PostForm(FlaskForm):
    content = TextAreaField(validators=[InputRequired()])
