from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
 
app = Flask(__name__)
app.secret_key = "super secret key" #necessary to prevent runtime error when handling sessions

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

            print (user)
            print (pw)

            if pw == 'password' and user == 'admin':
                session['logged_in'] = True
                return render_template('hub/hub.html')
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
        return render_template('hub/hub.html')
    

@app.route('/register', methods=['GET','POST'])
def do_register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    elif request.method == 'POST':
        return 'Hello World'
    
    
