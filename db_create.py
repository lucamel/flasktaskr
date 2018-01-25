import sqlite3
from _config import DATABASE_PATH

with sqlite3.connect(DATABASE_PATH) as connection:
    c = connection.cursor()

    c.execute('''create table tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL, due_date TEXT NOT NULL, priority INTEGER NOT NULL, status INTEGER NOT NULL)''')

    c.execute('''insert into tasks (name, due_date, priority, status)
        values('Finish this turorial', '25/01/2018', 10, 1)''')

    c.execute('''insert into tasks (name, due_date, priority, status)
        values('Finish Real Python Course 2', '25/01/2018', 10, 1)''')