import flask
import os
from raven import Client
import hashlib

from .datebase import query


class Auth(object):
    @classmethod
    def signin(cls, data):
        user = User(username=data[u'username'], password=data[u'password'])
        return user.is_valid()

    @classmethod
    def signup(cls, data):
        user = User(username=data[u'username'], password=data[u'password'])
        user.create()

    @classmethod
    def check_authorization(self):
        sentry_dsn = os.environ.get('SENTRY_DSN', '')
        sentry_client = Client(sentry_dsn)
        sentry_client.captureMessage(flask.request.headers)
        sentry_client.captureMessage(flask.request.data)
        return True


class User(object):
    query = query

    username = None
    password = None

    def __init__(self, username, password=u''):
        self.username = username
        md5 = hashlib.md5()
        md5.update(password)
        encrypted_password = md5.hexdigest()
        self.password = encrypted_password

    def exists(self):
        rv = self.query('select * from users where username="{}"'.format(self.username))
        return len(rv) > 0

    def create(self):
        if not self.exists():
            self.query(
                'insert into users (username, password) VALUES ("{}","{}");'.format(self.username, self.password))
        return True

    def is_valid(self):
        rv = self.query(
            'select * from users where username="{}" and password="{}"'.format(self.username, self.password))
        return len(rv) > 0