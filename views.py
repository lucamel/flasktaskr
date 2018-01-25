# project/views.py

import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from forms import AddTaskForm

# config

app = Flask(__name__)
app.config.from_object('_config')

# helper functions

def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to log in first.")
            return redirect(url_for('login'))
    return wrap

# route handler

# Login
@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('GoodBye', 'info')
    return redirect(url_for('login'))

# Logout
@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            flash('Invalid credential. Please try again.', 'error')
            return render_template('login.html')
        else:
            session['logged_in'] = True
            flash('Welcome!', 'success')
            return redirect(url_for('tasks'))
    return render_template('login.html')

# Show tasks
@app.route('/tasks/')
@login_required
def tasks():
    g.db = connect_db()
    cursor = g.db.execute('select name, due_date, priority, task_id from tasks where status = 1')

    open_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cursor.fetchall()]

    cursor = g.db.execute('select name, due_date, priority, task_id from tasks where status = 0')

    closed_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cursor.fetchall()]

    g.db.close()

    return render_template('tasks.html',
        form = AddTaskForm(request.form),
        open_tasks = open_tasks,
        closed_tasks = closed_tasks
        )

# Add a new task
@app.route('/add/', methods = ['POST'])
@login_required
def new_task():
    g.db = connect_db()

    name = request.form['name']
    due_date = request.form['due_date']
    priority = request.form['priority']

    if not name or not due_date or not priority:
        flash('All fields are required.', 'danger')
        return redirect(url_for('tasks'))
    else:
        g.db.execute('insert into tasks(name, due_date, priority, status) values(?, ?, ?, 1)', [
            name,
            due_date,
            priority
            ])
        g.db.commit()
        g.db.close()
        flash('New task created', 'success')
        return redirect(url_for('tasks'))

# Complete a task
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    g.db = connect_db()
    g.db.execute('update tasks set status = 0 where task_id = ' + str(task_id))
    g.db.commit()
    g.db.close()
    flash('Task completed!', 'success')
    return redirect(url_for('tasks'))

# Delete a task
@app.route('/delete/<int:task_id>/')
@login_required
def delete(task_id):
    g.db = connect_db()
    g.db.execute('delete from tasks where task_id = ' + str(task_id))
    g.db.commit()
    g.db.close()
    flash('Task deleted!', 'success')
    return redirect(url_for('tasks'))
