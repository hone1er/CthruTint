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
clients = db.clients
vehicles = db.vehicles
weather_tech_orders = db.weather_tech

queue = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###################################################################
"""
                                          \/  CLIENT CHECK IN  \/

"""
###################################################################
@app.route("/")
def index():
    return render_template('check_in.html')

# Handles main check in form from "/"(index()): add client to 'User' collection
@app.route("/form_submit", methods=['POST', 'GET'])
def form():
    response = request.form
    db_doc = {}

    # Remove any null values before inserting field in db_doc
    for k, v in response.items():
        if v != "":
            db_doc[k] = request.form.get(k)
    queue.append(db_doc['name'])
# Update User DB with client info
    clients.update(
                        {'client': request.form.get('name')},
                        db_doc, upsert=True)
    return redirect(url_for('index'))
###################################################################
"""
                                          \/  WEATHER TECH ORDER FORM  \/

"""
###################################################################
# Weather Tech order from page and form
@app.route("/weather_tech_order_form", methods=['GET', 'POST'])
def weather_tech_order_form():
    if request.method == 'POST':
           weather_tech_parts()
    return render_template('weather_tech.html')


def weather_tech_parts():
    """
    Uploads weather tech orders to 'weather_tech' collection
    """
    response = request.form
    db_doc = {}

    # Remove any null values before inserting field in db_doc
    parts = []
    for k, v in response.items():
        if v != "":
            if k[0:4] == "part":
                parts.append(v)
            else:
                db_doc[k] = request.form.get(k)
    db_doc['parts'] = parts

# Update DB
    weather_tech_order_form.insert_one(db_doc)
    return render_template('weather_tech.html')    
###################################################################
"""
                                     \/  VEHICLE CHECK  \/

"""
###################################################################
@app.route("/vehicle")
def vehicle():
    return render_template("vehicle_check.html")


@app.route("/vehicle_check", methods=['POST'])
def vehicle_form():
    response = request.form
    db_doc = {}

    # Remove any null values before inserting field in db_doc
    for k, v in response.items():
        if v != "":
            db_doc[k] = request.form.get(k)

# Update DB
    db.vehicles.insert(
                        db_doc
                        )

    return redirect(url_for('vehicle'))
    ###################################################################