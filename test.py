# project/test.py

import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)

        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, name, password):
        return self.app.post('/', data = dict(name = name, password = password), follow_redirects = True)

    def logout(self):
        return self.app.get('/logout/', follow_redirects = True)

    def register(self, name, email, password, confirm):
        return self.app.post('/register/', data = dict(name = name, email = email, password = password, confirm = confirm), follow_redirects = True)

    def create_user(self, name = 'johndoe', email = 'johndoe@example.com', password = 'secret'):
        new_user = User(name, email, password)
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


    def test_user_setup(self):
        new_user = User('lucamel', 'lucamel11@gmail.com', 'password')
        db.session.add(new_user)
        db.session.commit()
        user = db.session.query(User).all()
        for t in user:
            t.name
        assert t.name == 'lucamel'

    def test_login_form_is_present(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access your blog.', response.data)

    def test_unregistered_user_cannot_login(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid credential. Please try again.', response.data)

    def test_login_with_invalid_data(self):
        response = self.login('alert("alert box");', 'bar')
        self.assertIn(b'Invalid credential. Please try again.', response.data)

    def test_register_form_is_present(self):
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access task list.', response.data)
    
    def test_user_can_register(self):
        self.app.get('/register/', follow_redirects = True)
        response = self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.assertIn(b'Registration completed. You can login now!', response.data)

    def test_user_can_register_an_existing_username(self):
        self.app.get('/register/', follow_redirects = True)
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.app.get('/register/', follow_redirects = True)
        response = self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.assertIn(b'Username or email already exist.', response.data)

    def test_registered_user_can_login(self):
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        response = self.login('johndoe', 'mypassword')
        self.assertIn(b'Welcome, johndoe!', response.data)

    def test_logged_in_users_can_logout(self):        
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.login('johndoe', 'mypassword')
        response = self.logout()
        self.assertIn(b'Goodbye johndoe...', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye johndoe...', response.data)

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
        self.login(user.name, user.password)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.create_task(name = 'My new task')
        self.assertIn(b'My new task', response.data)

    def test_users_cannot_add_task_with_invalid_data(self):
        user = self.create_user()
        self.login(user.name, user.password)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.create_task(name = 'My new task', due_date = '')
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_task(self):
        user = self.create_user()
        self.login(user.name, user.password)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        response = self.app.get('/complete/1/', follow_redirects = True)
        self.assertIn(b'Task is complete. Good job!', response.data)

    def test_users_cannot_complete_task_that_are_not_created_by_them(self):
        user = self.create_user()
        self.login(user.name, user.password)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        self.logout()
        other_user = self.create_user(name = 'janedoe', email = 'jane@example.com')
        self.login(other_user.name, other_user.password)
        self.app.get('/tasks/', follow_redirects = True)
        response = self.app.get('/complete/1/', follow_redirects = True)
        self.assertNotIn(b'Task is complete. Good job!', response.data)

    def test_users_can_delete_task(self):
        user = self.create_user()
        self.login(user.name, user.password)
        self.app.get('/tasks/', follow_redirects = True)
        self.create_task()
        response = self.app.get('/delete/1/', follow_redirects = True)
        self.assertIn(b'Task deleted!', response.data)

if __name__ == '__main__':
    unittest.main()
