
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
    
    def login(self, name, password = 'mypassword'):
        return self.app.post('/', data = dict(
            name = name, 
            password = password
            ), 
        follow_redirects = True
        )

    def logout(self):
        return self.app.get('/logout/', follow_redirects = True)

    def register(self, name, email, password, confirm):
        return self.app.post('/register/', data = dict(
            name = name, 
            email = email, 
            password = password, 
            confirm = confirm
            ), 
        follow_redirects = True
        )

    def create_user(self, name = 'johndoe', email = 'johndoe@example.com', password = 'mypassword', role = 'user'):
        new_user = User(name, email, bcrypt.generate_password_hash(password), role)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def create_task(self, name = 'New Task', due_date = '01/01/2018', posted_date = '01/01/2018', priority = '1', status = '1'):
        return self.app.post('/tasks/', data = dict(
            name = name, 
            due_date = due_date, 
            posted_date = posted_date,
            priority = priority,
            status = status
            ), 
        follow_redirects = True
        )

    # Tests
    
    def test_logged_in_users_can_access_tasks_page(self):        
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.login('johndoe', 'mypassword')
        response = self.app.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open Tasks', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('/tasks/', follow_redirects = True)
        self.assertIn(b'You need to log in first.', response.data)

    def test_users_can_add_task(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.create_task(name = 'My new task')
        self.assertIn(b'My new task', response.data)

    def test_users_cannot_add_task_with_invalid_data(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.create_task(name = 'My new task', due_date = '')
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_task(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        response = self.app.get('/complete/1/', follow_redirects = True)
        self.assertIn(b'Task is complete. Good job!', response.data)

    def test_users_cannot_complete_task_that_are_not_created_by_them(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com')
        self.login(other_user.name)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.app.get('/complete/1/', follow_redirects = True)
        self.assertNotIn(b'Task is complete. Good job!', response.data)
        self.assertIn(b'You can only update yours tasks.', response.data)

    def test_admin_users_can_complete_task_that_are_not_created_by_them(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com', role = 'admin')
        self.login(other_user.name)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.app.get('/complete/1/', follow_redirects = True)
        self.assertIn(b'Task is complete. Good job!', response.data)
        self.assertNotIn(b'You can only update yours tasks.', response.data)

    def test_users_can_delete_task(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        response = self.app.get('/delete/1/', follow_redirects = True)
        self.assertIn(b'Task deleted!', response.data)

    def test_users_cannot_delete_task_that_are_not_created_by_them(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com')
        self.login(other_user.name)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.app.get('/delete/1/', follow_redirects = True)
        self.assertNotIn(b'Task deleted!', response.data)
        self.assertIn(b'You can only delete yours tasks.', response.data)

    def test_admin_users_can_delete_task_that_are_not_created_by_them(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com', role = 'admin')
        self.login(other_user.name)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.app.get('/delete/1/', follow_redirects = True)
        self.assertIn(b'Task deleted!', response.data)
        self.assertNotIn(b'You can only delete yours tasks.', response.data)

    def test_string_representation_of_the_task_object(self):
        new_task = self.create_task()
        tasks = db.session.query(Task).all()
        for task in tasks:
            self.assertEqual(str(task), '<Task: {}>'.format(new_task.name))

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com')
        response = self.login(other_user.name)
        self.assertNotIn(b'Complete', response.data)
        self.assertNotIn(b'Delete', response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com')
        self.login(other_user.name)
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'complete/2/', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        user = self.create_user()
        self.login(user.name)
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com', role = 'admin')
        self.login(other_user.name)
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)

if __name__ == '__main__':
    unittest.main()
