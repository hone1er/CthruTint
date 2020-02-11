from flask import Flask, render_template, request, flash, redirect, url_for
from pymongo import MongoClient
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from config import SECRET_KEY
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("/"+os.path.dirname('__file__'), 'static/import')
ALLOWED_EXTENSIONS = {'jpeg', 'png', 'jpg', '.jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

conn = 'localhost:27017'
client = MongoClient(conn)
db = client.cThru
users = db.clients


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template('check_in.html')

# Handles main check in form from "/"(index())
@app.route("/form_submit", methods=['POST', 'GET'])
def form():
    response = request.form
    db_doc = {}

    # Remove any null values before inserting field in db_doc
    for k, v in response.items():
        if v != "":
            db_doc[k] = request.form.get(k)

# Update DB
    db.users.update(
                        {'client': request.form.get('name')},
                        db_doc, upsert=True)
    return redirect(url_for('index'))

@app.route("/weather_tech_order_form")
def weather_tech_order_form():
    return render_template('weather_tech.html')

@app.route("/vehicle")
def vehicle_check():
    return render_template('vehicle_check.html')

@app.route("/vehicle_checked", methods=['POST'])
def vehicle_form():
    response = request.form
    db_doc = {}

    # Remove any null values before inserting field in db_doc
    for k, v in response.items():
        if v != "":
            db_doc[k] = request.form.get(k)

# Update DB
    db.vehicles.update(
                        {'vin': request.form.get('vin')},
                        db_doc, upsert=True)
    return redirect(url_for('vehicle_check'))