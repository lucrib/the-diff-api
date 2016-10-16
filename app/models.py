from app import db


class DiffModel(db.Model):
    __tablename__ = "DIFF"
    id = db.Column('id', db.Integer, primary_key=True, nullable=False)
    side = db.Column('side', db.String, primary_key=True, nullable=False)
    data = db.Column('data', db.String, nullable=False)

    def __init__(self, id, side, data):
        self.id = id
        self.side = side
        self.data = data

    def __repr__(self):
        return '<id:%d, side:%s>' % (self.id, self.side)

    def str(self):
        d = {
            'id': self.id,
            'side': self.side,
            'data': self.data
        }
        return d
