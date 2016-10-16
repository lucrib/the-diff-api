# from rest_api import db, DiffModel, app
#
# db.create_all()
# db.session.commit()

import sqlite3
from rest_api import app, db

conn = sqlite3.connect(app.config['DATABASE_PATH'])
conn.close()
db.create_all()

# if not os.path.exists(DATABASE_PATH):
#     api.create(DATABASE_PATH, 'database repository')
#     api.version_control(SQLALCHEMY_DATABASE_URI, DATABASE_PATH)
