from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_socketio import SocketIO
from database import db_get_user, db_add_user, db_validate_user, db_user_exists
from random import randint
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

            if db_validate_user(user,pw):
                session['logged_in'] = True
              
                pid = nextPlayerId
                x = 8 
                y = 8
                seeker = len(players) == 0

                p = Player(pid, user, x, y, seeker)
                players[pid] = p

                msg = json.dumps(p.__dict__)

                session['mypid'] = pid
                session['myname'] = user
                nextPlayerId = nextPlayerId + 1

                socketio.emit('player_conn', msg, broadcast = True)

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
        return redirect('/login')
    else:
        pid = session.get('mypid')
        name = session.get('myname')
        return render_template('hub/hub.html', myPidArg = str(pid), myNameArg = name)

@socketio.on('disconnect')
def handle_disconnect():
    pid = session.get('mypid')
    if pid in players.keys():
      del players[pid]
      
    # TODO: what if the player is the only seeker? pick one at random and promote to seeker
    socketio.emit('player_disc', json.dumps(pid), broadcast = True)

@socketio.on('position_update')
def handle_position_update(data):
    posInfo = json.loads(data)
    pid = session.get('mypid')
    
    if pid in players.keys():
        p0 = players[pid]
        
        p0.x = posInfo['x']
        p0.y = posInfo['y']
    
        msg = json.dumps({'pid': pid, 'x': posInfo['x'], 'y': posInfo['y'] })
        socketio.emit('position_player_changed', msg, broadcast = True)
    
        # check if this seeker has catched another hider
        for pid, p in players.items():
          # only check if either one is a seeker 
          if (p0.seeker and not p.seeker) or (not p0.seeker and p.seeker):
            # distance (manhattan) maximum 1 square
            if p0.calculate_man_distance(p) <= 1:
              # update to seeker
              p.seeker = True
              # notify all clients
              socketio.emit('new_seeker', json.dumps(pid), broadcast = True)

    seekerCount = len([p for p in players.values() if p.seeker])
    playerCount = len(players)

    # check if all players are seekers now, if yes, revert back to 1 seeker
    # only check this if there are more than 1 players!
    if (seekerCount == playerCount and playerCount > 1) or (seekerCount == 0):
      randomSeekerIdx = randint(0, playerCount-1)
      pks = list(players.keys())
      randomSeekerPid = pks[randomSeekerIdx]
      msg = []
      
      for pid, p in players.items():
        p.seeker = True
        if not pid == randomSeekerPid:
          p.seeker = False
          p.x = 8
          p.y = 8
        else:
          p.x = 22
          p.y = 6

        msg.append(json.dumps({'pid': pid, 'seeker': p.seeker, 'x': p.x, 'y': p.y}))
        
      # notify all clients about reset seekers
      socketio.emit('reset_seekers', json.dumps(msg), broadcast = True)

@socketio.on('gamestate_request')
def handle_gamestate():
    global players

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
        pwd = request.form['psw']
        if pwd != request.form['psw-repeat']:
            return 'Passwords do not equal'
        if db_user_exists(email):
            return 'Username already exists'
        
        db_add_user(email, pwd, name)
        session['logged_in'] = True
        session['name'] = name
        return redirect('/')