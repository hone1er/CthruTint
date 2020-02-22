from wtforms import Form, StringField, DateField, validators, FileField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, widgets
import datetime
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from pymongo import MongoClient



class User(UserMixin):
    def __init__(self, username=None, email=None, password=None):
        # CONNECT TO MONGODB

        conn = 'localhost:27017'
        client = MongoClient(conn)
        self.db = client.cThru
        self.username = username
        self.password = password
        self.email = email

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def add_user(self):
        self.db.users.insert_one(
            {'username': self.username, 'password': self.password, 'email': self.email})

    def find_email(self, email):
        if self.db.users.count_documents({'email': email.data}) > 0:
            return 1
        return None

    def find_user(self, user):
        if self.db.users.count_documents({'username': user.data}) > 0:
            return 1
        return None

    def get_user(self):
        return self.username

    def get_name(self):
        return self.username

    def get_id(self):
        return self.username

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[validators.DataRequired(), validators.Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[
                             validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[validators.DataRequired(), validators.EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User().find_user(username)
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User().find_email(email)
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[validators.DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[
                             validators.DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')