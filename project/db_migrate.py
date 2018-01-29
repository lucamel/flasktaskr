
# project/db_migrate.py

from views import db
from _config import DATABASE_PATH

import sqlite3
from datetime import datetime


# with sqlite3.connect(DATABASE_PATH) as connection:
#     c = connection.cursor()

#     c.execute('alter table tasks rename to old_tasks')

#     # create the database and the table
#     db.create_all()

#     c.execute('select name, due_date, priority, status from old_tasks order by task_id asc')

#     data = [(row[0], row[1], row[2], row[3], datetime.now(), 1) for row in c.fetchall()]

#     c.executemany('insert into tasks(name, due_date, priority, status, posted_date, user_id) values(?, ?, ?, ?, ?, ?)', data)

#     c.execute('drop table old_tasks')

with sqlite3.connect(DATABASE_PATH) as connection:
    c = connection.cursor()

    c.execute('alter table users rename to old_users')

    # create the database and the table
    db.create_all()

    c.execute('select name, email, password from old_users order by user_id asc')

    data = [(row[0], row[1], row[2], 'user') for row in c.fetchall()]

    c.executemany('insert into users(name, email, password, role) values(?, ?, ?, ?)', data)

    c.execute('drop table old_users')