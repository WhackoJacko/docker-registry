import flask
import hashlib
import base64
import uuid
import re
import boto
boto.s3

from .database import query

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(u'auth.log'))


class Auth(object):
    @staticmethod
    def query(*args, **kwargs):
        return query(*args, **kwargs)

    @classmethod
    def signin(cls, data):
        user = User(username=data[u'username'], password=data[u'password'])
        return user.is_valid()

    @classmethod
    def signup(cls, data):
        user = User(username=data[u'username'], password=data[u'password'])
        return user.create()

    @classmethod
    def check_authorization(self):
        authorization_header = flask.request.headers.get(u'Authorization', u'')
        if authorization_header.startswith(u'Basic'):
            authorization_token = authorization_header.split(u' ').pop()
            authorization_token_decoded = base64.b64decode(authorization_token)
            username, password = authorization_token_decoded.split(u':')
            if username and password:
                user = User(username=username, password=password)
                return user.is_valid()
        return False

    @classmethod
    def generate_token(cls):
        token = uuid.uuid1().get_hex()
        query(u'insert into tokens (token) VALUES (?);', args=(token,))
        return token

    @classmethod
    def validate_token(cls):
        authorization_header = flask.request.headers.get(u'Authorization', u'')
        p = re.compile(u'.*signature=(.*?),')
        res = p.match(authorization_header)
        if res:
            token = res.groups()[0]
            rv = query(u'select * from tokens where token=?', args=(token,))
            return len(rv) > 0
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