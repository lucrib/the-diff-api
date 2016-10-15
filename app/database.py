import os
from app import db


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


class DiffSideModel(db.Model):
    id = db.Column(db.Integer)
    side = db.Column(db.String)
    data = db.Column(db.String)
