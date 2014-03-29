import flask
import hashlib
import base64

from .database import query

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(u'auth.log'))


class Auth(object):
    @classmethod
    def signup(cls, data):
        user = User(username=data[u'username'], password=data[u'password'])
        return user.create()

    @classmethod
    def check_authorization(self):
        authorization_token = flask.request.headers.get(u'Authorization', u'').split(u' ').pop()
        if authorization_token:
            authorization_token_decoded = base64.b64decode(authorization_token)
            username, password = authorization_token_decoded.split(u':')
            if username and password:
                user = User(username=username, password=password)
                return user.is_valid()
        return False


class User(object):
    @staticmethod
    def query(*args, **kwargs):
        return query(*args, **kwargs)

    username = None
    password = None

    def __init__(self, username, password=u''):
        self.username = username
        md5 = hashlib.md5()
        md5.update(password)
        encrypted_password = md5.hexdigest()
        self.password = encrypted_password

    def exists(self):
        query_str = u'select * from users where username=?'
        args = (self.username,)
        rv = self.query(query_str, args=args)
        return len(rv) > 0

    def create(self):
        query_str = u'insert into users (username, password) VALUES (?,?);'
        args = (self.username, self.password)
        if not self.exists():
            self.query(query_str, args=args)
            return True
        return False

    def is_valid(self):
        query_str = u'select * from users where username=? and password=?'
        args = (self.username, self.password)
        rv = self.query(query_str, args)
        return len(rv) > 0