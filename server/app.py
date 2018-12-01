from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_socketio import SocketIO
from database import db_get_user, db_add_user, db_validate_user, db_user_exists
import os

app = Flask(__name__)

# disable caching while in development mode
app.config["CACHE_TYPE"] = "null"

# necessary to prevent runtime error when handling sessions
app.secret_key = "super secret key"

# required for websockets
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('auth/login.html')
    else:
        return render_template('hub/hub.html')
 
@app.route('/login', methods=['POST'])
def do_login():
    if request.method == 'POST':
        if not session.get('logged_in'):
            pw = request.form['password']
            user = request.form['username']

            if db_validate_user(user,pw):
                session['logged_in'] = True
                return redirect('/hub')
            else:
                return "wrong password!"
        else:
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/hub')
def hub():
    if not session.get('logged_in'):
        return render_template('auth/login.html')
    else:
        return render_template('hub/hub.html')

@socketio.on('json')
def handle_json(json):
    print('received json on websocket: ' + str(json))

@socketio.on('message')
def handle_message(message):
    print('received message on websocket: ' + message)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@app.route('/register', methods=['GET','POST'])
def do_register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    elif request.method == 'POST':
        name = request.form['display_name']
        email = request.form['email']
        pwd = request.form['psw']
        if pwd != request.form['psw-repeat']:
            return 'Passwords do not equal'
        if db_user_exists(email):
            return 'Username already exists'
        
        db_add_user(email, pwd, name)
        session['logged_in'] = True
        session['name'] = name
        return redirect('/')

    