
# db_create.py

from datetime import date

from project import db
from project.models import Task


# create the database and the db table
db.create_all()

# insert data
# db.session.add(User('admin', 'admin@example.com', 'admin', 'admin')
# db.session.add(Task('Finish this tutorial', date(2018, 1, 29), 10, 1))
# db.session.add(Task('Finish Real Python', date(2018, 1, 29), 10, 1))

# commit the changes
db.session.commit()