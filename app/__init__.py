from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from app.rest_api import DiffApi, DiffSidesApi


app = Flask(__name__, static_url_path="")
app.config.from_object('database')
api = Api(app)
db = SQLAlchemy(app)

from app import database

api.add_resource(DiffApi, '/v1/diff/<int:id>', endpoint='diff')
# Instead of having two different endpoints for the same purpose, it easier to transform the side in a parameter
# The parameter is treated inside method calls
api.add_resource(DiffSidesApi, '/v1/diff/<int:id>/<string:side>', endpoint='side')
