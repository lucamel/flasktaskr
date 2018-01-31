
# project/_config.py

import os

# grab the folder
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
WTF_CSRF_ENABLED = True
SECRET_KEY = b'\xb0m\xba$z\xae\xb8\xff\r\x81\x02\x93\xc8\xe8\x04X\x0e\xb8\xdeM\xc4\xa2|\xa6'
DEBUG = False
DATABASE_PATH = os.path.join(basedir, DATABASE)

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + DATABASE_PATH)
SQLALCHEMY_TRACK_MODIFICATIONS = False