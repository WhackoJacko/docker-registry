import sqlite3
from flask import g

DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query(query, args=(), one=False):
    print(query())
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init():
    query('create table if not exists users(username varchar(256), password varchar(32));')


init()