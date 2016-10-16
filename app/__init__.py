import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path="")
api = Api(app)
db = SQLAlchemy(app)

import models

try:
    db_name = app.config['DATABASE']
except KeyError:
    app.config['DATABASE'] = './database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']


if not os.path.isfile(app.config['DATABASE']):
    db.create_all()

from app.rest_api import DiffApi, DiffSidesApi

api.add_resource(DiffApi, '/v1/diff/<int:id>', endpoint='diff')
# Instead of having two different endpoints for the same purpose, it easier to transform the side in a parameter
# The parameter is treated inside method calls
api.add_resource(DiffSidesApi, '/v1/diff/<int:id>/<string:side>', endpoint='side')


def clear_db():
    db.drop_all()
    db.create_all()
app.clear_db = clear_db