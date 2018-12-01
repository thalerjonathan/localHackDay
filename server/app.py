from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_socketio import SocketIO
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
        return render_template('auth/socket.html')
 
@app.route('/login', methods=['POST'])
def do_login():
    if request.method == 'POST':
        if not session.get('logged_in'):
            pw = request.form['password']
            user = request.form['username']

            if pw == 'password' and user == 'admin':
                session['logged_in'] = True
                return render_template('auth/socket.html')
            else:
                print ("wrong password!")
        else:
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/hub')
def hub():
    if not session.get('logged_in'):
        return render_template('auth/login.html')
    else:
        return render_template('auth/socket.html')

@socketio.on('json')
def handle_json(json):
    print('received json on websocket: ' + str(json))

@socketio.on('message')
def handle_message(message):
    print('received message on websocket: ' + message)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))