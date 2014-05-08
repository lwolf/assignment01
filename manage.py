# coding: utf-8

from flask.ext.script import Manager
from watchapp.app import app
from watchapp.extensions import db

manager = Manager(app)

@manager.command
def initdb():
    db.create_all()


@manager.command
def dropdb():
    db.drop_all()


@manager.command
def initial_sync():
    pass


if __name__ == '__main__':
    manager.run()