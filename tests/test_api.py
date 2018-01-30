
# tests/test_tasks.py

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User, Task
from datetime import date

TEST_DB = 'test.db'

class TasksTests(unittest.TestCase):

    # SetUp and TearDown

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False        
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)

        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper functions
    
    def add_tasks(self):
        db.session.add(
            Task(
                'First Task',
                date(2018, 1, 1),
                10,
                date(2018, 1, 1),
                1,
                1
            )
        )
        db.session.commit()

        db.session.add(
            Task(
                'Second Task',
                date(2018, 1, 10),
                10,
                date(2018, 1, 10),
                1,
                1
            )
        )
        db.session.commit()

    # Tests

    def test_collection_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn(b'First Task', response.data)
        self.assertIn(b'Second Task', response.data)

    def test_resource_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/2', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn(b'Second Task', response.data)
        self.assertNotIn(b'First Task', response.data)

    def test_invalid_resource_endpoint_returns_error(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/209', follow_redirects=True)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn(b'Element does not exist', response.data)

if __name__ == '__main__':
    unittest.main()
