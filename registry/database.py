import os
import sqlite3

from flask import g

DATABASE = os.path.join(os.path.dirname(__file__), u'..', u'database.db')


def get_db():
    db = getattr(g, u'_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        init()
    return db


def query(query_str, args=(), one=False):
    db = get_db()
    cur = db.cursor().execute(query_str, args)
    rv = cur.fetchall()
    db.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init():
    query(
        u'create table if not exists users(id integer primary key '
        u'autoincrement, username varchar(256), password varchar(32));'
    )
    query(u'create table if not exists tokens(token varchar(32));')