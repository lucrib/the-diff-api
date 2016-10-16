import sqlite3
from rest_api import app, db

conn = sqlite3.connect(app.config['DATABASE_PATH'])
conn.close()
db.create_all()
