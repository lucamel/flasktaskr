
# project/users/views.py

from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from .forms import RegisterForm, LoginForm
from project import db, bcrypt
from project.models import User
from pprint import pprint

# Config

users_blueprint = Blueprint('users', __name__)

# Helper functions

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to log in first.", "warning")
            return redirect(url_for('users.login'))
    return wrap

def guest(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return test(*args, **kwargs)
        else:
            return redirect(url_for('tasks.tasks'))
    return wrap

# Routes

# Logout
@users_blueprint.route('/logout/')
@login_required
def logout():
    user = User.query.filter_by(user_id = session['user_id']).first()
    flash('Goodbye {}...'.format(user.name), 'info')
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('name', None)
    return redirect(url_for('users.login'))

# Login
@users_blueprint.route('/', methods = ['GET', 'POST'])
@guest
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name = request.form['name']).first()
            if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
                session['logged_in'] = True
                session['user_id'] = user.user_id
                session['role'] = user.role
                session['name'] = user.name
                flash('Welcome, {}!'.format(user.name), 'success')
                return redirect(url_for('tasks.tasks'))
            else:
                error = 'Invalid credential. Please try again.'
    return render_template('login.html', form = form, error = error)

# Register
@users_blueprint.route('/register/', methods = ['GET', 'POST'])
@guest
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.name.data,
                form.email.data,
                bcrypt.generate_password_hash(form.password.data)
                )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration completed. You can login now!', 'success')
                return redirect(url_for('users.login'))
            except IntegrityError:
                error = 'Username or email already exist.'
    return render_template('register.html', form = form, error = error)