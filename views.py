# project/views.py

from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm
import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

# config

app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User

# helper functions

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to log in first.", "warning")
            return redirect(url_for('login'))
    return wrap

# route handler

# Login
@app.route('/logout/')
def logout():
    user = User.query.filter_by(user_id = session['user_id']).first()
    flash('Goodbye {}...'.format(user.name), 'info')
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Register
@app.route('/register/', methods = ['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data
                )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration completed. You can login now!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form = form, error = error)

# Logout
@app.route('/', methods = ['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name = request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.user_id
                flash('Welcome, {}!'.format(user.name), 'success')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid credential. Please try again.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html', form = form, error = error)

# Show tasks
@app.route('/tasks/')
@login_required
def tasks():
    open_tasks = db.session.query(Task).filter_by(status = '1').order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task).filter_by(status = '0').order_by(Task.due_date.asc())
    return render_template('tasks.html',
        form = AddTaskForm(request.form),
        open_tasks = open_tasks,
        closed_tasks = closed_tasks
        )

# Add a new task
@app.route('/add/', methods = ['GET', 'POST'])
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                datetime.datetime.utcnow(),
                '1',
                session['user_id']
                )
            db.session.add(new_task)
            db.session.commit()
            flash('New task created', 'success')
        return redirect(url_for('tasks'))
    return redirect(url_for('tasks'))

# Complete a task
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    complete_id = task_id
    db.session.query(Task).filter_by(task_id = complete_id).update({'status': '0'})
    db.session.commit()
    flash('Task is complete. Good job!', 'success')
    return redirect(url_for('tasks'))

# Delete a task
@app.route('/delete/<int:task_id>/')
@login_required
def delete(task_id):
    delete_id = task_id
    db.session.query(Task).filter_by(task_id = delete_id).delete()
    db.session.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('tasks'))
