
# project/tasks/views.py

import datetime
from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from .forms import AddTaskForm
from project import db
from project.models import Task

# Config

tasks_blueprint = Blueprint('tasks', __name__)

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

def open_tasks():
    return db.session.query(Task).filter_by(status = '1').order_by(Task.due_date.asc())

def closed_tasks():
    return db.session.query(Task).filter_by(status = '0').order_by(Task.due_date.asc())

# Add a new task
def new_task():
    error = None
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
            flash('New task created!', 'success')
            return redirect(url_for('tasks.tasks'))
    return render_template('tasks.html', form = form, error = error, open_tasks = open_tasks(), closed_tasks = closed_tasks())

# Routes

# Show tasks
@tasks_blueprint.route('/tasks/', methods = ['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        return new_task()
    return render_template('tasks.html',
        form = AddTaskForm(request.form),
        open_tasks = open_tasks(),
        closed_tasks = closed_tasks()
        )

# Complete a task
@tasks_blueprint.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    task_to_complete_id = task_id
    task = db.session.query(Task).filter_by(task_id = task_to_complete_id)
    if session['role'] == 'admin' or session['user_id'] == task.first().user_id:
        task.update({'status' : '0'})
        db.session.commit()
        flash('Task is complete. Good job!', 'success')
    else:
        flash('You can only update yours tasks.')
    return redirect(url_for('tasks.tasks'))

# Delete a task
@tasks_blueprint.route('/delete/<int:task_id>/')
@login_required
def delete(task_id):
    task_to_delete_id = task_id
    task = db.session.query(Task).filter_by(task_id = task_to_delete_id)
    if session['role'] == 'admin' or session['user_id'] == task.first().user_id:
        task.delete()
        db.session.commit()
        flash('Task deleted!', 'success')    
    else:
        flash('You can only delete yours tasks.')
    return redirect(url_for('tasks.tasks'))