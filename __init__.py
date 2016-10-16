# import os
# from rest_api import db, app
#
#
# # A simple database creation
# try:
#     db_name = app.config['DATABASE']
# except KeyError:
#     app.config['DATABASE'] = './database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
# if not os.path.isfile(app.config['DATABASE']):
#     db.create_all()
#
#
# def clear_db():
#     db.drop_all()
#     db.create_all()
#
# app.clear_db = clear_db
