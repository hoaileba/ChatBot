import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext
# print('vcl    ', current_app.config['DATABASE'])
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    # g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('MyProj/models/database.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def getCount():
    data = get_db()
    c = data.execute('select count (id_dia) as cnt from rest_dialogue').fetchone()['cnt']
    c+=1
    return c


def addInit():
    c = getCount()
    data = get_db()
    print(type(c))
    
    data.execute('insert into rest_dialogue(id_dia) values (?)',(c,))
    data.commit()


def getAllObjectReq(id):
    data = get_db()
    last = data.execute('select id_re,id_dia_id from rest_request_dia where id_dia_id = (?)',(id,)).fetchall()

    return (len(last))

def getLastRep(id):
    data = get_db()
    last = data.execute('select * from rest_request_dia where id_dia_id = (?)',(id,)).fetchall()
    return last[-1]


def getAnsChamp(champ):
    data = get_db()
    last = data.execute('select * from rest_ans where champ = (?)',(champ,)).fetchall()
    return last[0]
def addReq(req,hero,skill,id_dia_id,intent, action):
    data = get_db()
    data.execute('insert into rest_request_dia(req,hero,skill,id_dia_id,intent,action) values (?,?,?,?,?,?)',(req,hero,skill,id_dia_id,intent,action,))
    data.commit()
