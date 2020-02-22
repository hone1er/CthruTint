from flask import Flask, render_template, request, flash, redirect, url_for
from pymongo import MongoClient
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
import os
from myForms import RegistrationForm, LoginForm, User






app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.secret_key = '0\xeeuI\xae\xb2\x04i\x8f,t\xdecz\xb5\x11\xd9J\xa9fn\xfahb'


login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



conn = 'localhost:27017'
client = MongoClient(conn)
db = client.cThru
clients = db.clients
vehicles = db.vehicles
weather_tech_orders = db.weather_tech



########### LOGIN/REGISTRATION/LOGOUT ##################

@login_manager.user_loader
def load_user(username):
    u = db.users.find_one({"username": username})
    if not u:
        return None
    return User(username=u['username'], email=u['email'])


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('income'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        user.add_user()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("5/minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('income'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.users.find_one({'email': form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            user = User(username=user['username'],
            email=user['email'])
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('show'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

######################################################################################






def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/show_submit", methods=['POST'])
@login_required
def show_form():
    if request.method == 'POST':
        response = request.form
        db_doc = {}

        # Remove any null values and set strings to lowercase before inserting field in db_doc
        for k, v in response.items():
            if v != "":
                if type(v) == str:
                    db_doc[k] = request.form.get(k).lower()
                else:
                    db_doc[k] = request.form.get(k)

        # Add customer to the queue
        db_doc['queued'] = True

        # Update User DB with client info
        db.show_form.update(
            {
                'client': db_doc['client']
                },
                db_doc,
                upsert=True
                )
        return redirect(url_for('show'))
###################################################################
"""
                                          \/  CLIENT CHECK IN  \/

"""
###################################################################
# Handles main check in form from "/"(check_in()): add client to 'User' collection
@app.route("/form_submit", methods=['POST'])
@login_required
def form():
    if request.method == 'POST':
        response = request.form
        db_doc = {}

        # Remove any null values and set strings to lowercase before inserting field in db_doc
        for k, v in response.items():
            if v != "":
                if type(v) == str:
                    db_doc[k] = request.form.get(k).lower()
                else:
                    db_doc[k] = request.form.get(k)

        # Add customer to the queue
        db_doc['queued'] = True

        # Update User DB with client info
        clients.find_one_and_update(
            {
                'client': db_doc['client']
                },
                {'$set': db_doc,
                '$inc': {'visits': 1}},
                upsert=True
                )
        return redirect(url_for('check_in'))
###################################################################
"""
                                     \/  SELECT CUSTOMER FROM QUEUE  \/

"""
###################################################################

@app.route("/vehicle_inspection", methods=['POST'])
@login_required
def vehicle_inspection():
    if request.method == 'POST':
        name = request.form.get('customer')
        print(name)
        return render_template('vehicle_check.html', name=name)
###################################################################
"""
                                     \/  VEHICLE CHECK  \/

"""
###################################################################
@app.route("/vehicle_check", methods=['POST'])
@login_required
def vehicle_form():
    response = request.form
    db_doc = {}

    # Remove any null values before inserting field in db_doc
    for k, v in response.items():
        if v != "":
            db_doc[k] = request.form.get(k)
    print(db_doc)
    # Update DB
    name = db_doc['client']
    del db_doc['client']
    
    clients.update(
        {'client': name},
        {'$set': {'queued': False},
        '$push': {'vehicles': db_doc}
        })
    return redirect(url_for('queue'))
###################################################################
###################################################################
"""
                                          \/  WEATHER TECH ORDER FORM  \/

"""
###################################################################
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
    
# Weather Tech order from page and form
@app.route("/weather_tech_order_form", methods=['GET', 'POST'])
def weather_tech_order_form():
    if request.method == 'POST':
           weather_tech_parts()
    return render_template('weather_tech.html')


    

@app.route("/")
@login_required
def check_in():
    return render_template('check_in.html')


@app.route("/queue")
@login_required
def queue():
    queue = clients.find({'queued': True})
    return render_template("queue.html", queue=queue)

@app.route("/show")
@login_required
def show():
    return render_template('shows.html')
