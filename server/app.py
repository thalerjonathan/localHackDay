from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
 
app = Flask(__name__)
 
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('auth/login.html')
    else:
        return "Hello Boss!"
 
@app.route('/login', methods=['POST'])
def do_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return "Hello Boss!"
    else:
        flash('wrong password!')
    return home()