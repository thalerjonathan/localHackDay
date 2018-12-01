from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_socketio import SocketIO
from database import db_get_user, db_add_user, db_validate_user, db_user_exists
import os
import json

from player import Player

app = Flask(__name__)

# disable caching while in development mode
app.config["CACHE_TYPE"] = "null"

# necessary to prevent runtime error when handling sessions
app.secret_key = "super secret key"

# required for websockets
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

nextPlayerId = 0
players = {}

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        return redirect('/hub')
 
@app.route('/login', methods=['GET', 'POST'])
def do_login():
    global nextPlayerId
    global players

    if request.method == 'POST':
        if not session.get('logged_in'):
            pw = request.form['password']
            user = request.form['username']

            if pw == 'password' and user == 'admin':
                session['logged_in'] = True
              
                pid = nextPlayerId
                x = 8
                y = 8
                nextPlayerId = nextPlayerId + 1

                p = Player(pid, user, x, y)
                players[pid] = p

                msg = json.dumps(p.__dict__)

                socketio.emit('player_conn', msg, broadcast = True)

                session['mypid'] = pid
                return redirect('/hub')

            else:
                print ("wrong password!")
        else:
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/hub')
def hub():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        pid = session.get('mypid')
        return render_template('hub/hub.html', myPidArg = str(pid))

@socketio.on('disconnect')
def handle_disconnect():
    # TODO: get correct playerId from session and send in broadcast
    socketio.emit('player_disc', '{ playerId: '', playerData = '' }', broadcast = True)

@socketio.on('gamestate_request')
def handle_gamestate():
    global players

    print ("gamestate_request")
    print (players)

    msg = []
    for pid, p in players.items():
      msg.append(json.dumps(p.__dict__))
      
    socketio.emit('gamestate_reply', json.dumps(msg))

@app.route('/register', methods=['GET','POST'])
def do_register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    elif request.method == 'POST':
        name = request.form['display_name']
        email = request.form['email']
        pwd = request.form['psw'].encode('utf-8')
        if pwd != request.form['psw-repeat'].encode('utf-8'):
            return 'Passwords do not equal'
        
        if db_user_exists(email):
            return 'Username already exists'
        
        db_add_user(email,pwd,name)
        session['logged_in'] = True
        return session['logged_in']
        return redirect('/')    
        
        return render_template('auth/register.html')
    