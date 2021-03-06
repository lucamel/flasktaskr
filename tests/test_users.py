
# tests/test_users.py

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'

class UsersTests(unittest.TestCase):

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

    # Tests

    def test_users_can_be_added_to_db(self):
        new_user = User('johndoe', 'johndoe@example.com', bcrypt.generate_password_hash('mypassword'))
        db.session.add(new_user)
        db.session.commit()
        user = db.session.query(User).all()
        for t in user:
            t.name
        assert t.name == 'johndoe'

    def test_login_form_is_present(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access your blog.', response.data)

    def test_registered_user_can_login(self):
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        response = self.login('johndoe', 'mypassword')
        self.assertIn(b'Welcome, johndoe!', response.data)
    
    def test_logged_in_users_must_seen_their_name(self):
        user = self.create_user(name = 'johndoe')
        self.login(user.name)
        response = self.app.get('/tasks/', follow_redirects = True)
        self.assertIn(b'johndoe', response.data)

    def test_logged_in_users_cannot_access_login_page(self):
        user = self.create_user()
        self.login(user.name)
        response = self.app.get('/', follow_redirects = True)
        self.assertNotIn(b'Please log in to access your blog.', response.data)
        self.assertIn(b'Open Tasks', response.data)

    def test_unregistered_user_cannot_login(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid credential. Please try again.', response.data)

    def test_login_with_invalid_data(self):
        response = self.login('alert("alert box");', 'bar')
        self.assertIn(b'Invalid credential. Please try again.', response.data)

    def test_login_with_fields_error(self):
        response = self.login('', 'bar')
        self.assertIn(b'This field is required.', response.data)

    def test_register_form_is_present(self):
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access task list.', response.data)
    
    def test_user_can_register(self):
        self.app.get('/register/', follow_redirects = True)
        response = self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.assertIn(b'Registration completed. You can login now!', response.data)

    def test_user_cannot_register_an_existing_username(self):
        self.app.get('/register/', follow_redirects = True)
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.app.get('/register/', follow_redirects = True)
        response = self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.assertIn(b'Username or email already exist.', response.data)

    def test_logged_in_users_can_logout(self):        
        self.register('johndoe', 'john@example.com', 'mypassword', 'mypassword')
        self.login('johndoe', 'mypassword')
        response = self.logout()
        self.assertIn(b'Goodbye johndoe...', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye johndoe...', response.data)

    def test_default_user_role(self):
        new_user = self.create_user()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role, 'user')
        
    def test_string_representation_of_the_user_object(self):
        new_user = self.create_user()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(str(user), '<User: {}>'.format(new_user.name))

if __name__ == '__main__':
    unittest.main()
