import base64
import json
import sqlalchemy.exc
from flask import Flask, jsonify, abort, make_response
from flask_restful import Resource, reqparse, Api
from flask_sqlalchemy import SQLAlchemy


# Creates the Flask app
app = Flask(__name__, static_url_path="")
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
api = Api(app)


# DATA MODELS

class DiffModel(db.Model):
    """
    The model that represents a 'diff side data' in the database
    """
    __tablename__ = "DIFF"
    id = db.Column('id', db.Integer, primary_key=True, nullable=False)
    side = db.Column('side', db.String, primary_key=True, nullable=False)
    data = db.Column('data', db.String, nullable=False)

    def __init__(self, id, side, data):
        """
        Creates a new DiffModel object that can be used to operate the database
        :param id: The data ID
        :param side: The data SIDE
        :param data: The data itself
        """
        self.id = id
        self.side = side
        self.data = data

    def __repr__(self):
        return '<id:%d, side:%s>' % (self.id, self.side)

    def __str__(self):
        d = {
            'id': self.id,
            'side': self.side,
            'data': self.data
        }
        return d


# THE DIFF LOGIC

def diff(left, right):
    """
    The diff generator

    The possible returns are:
    -2 and  Error message if an exception happens
    -1 and warning message if the data sizes are diferent
    0 and message if the data are equals
    >= 1 the code will be amount of diffs found and the message will be the diffs

    :param left: The left data
    :param right: The right data
    :return: A tuple containing the return code and diffs/message when applicable
    :rtype: tuple
    """
    try:
        l = base64.b64decode(left)
        r = base64.b64decode(right)
    except Exception as e:
        return -2, unicode(e.message)
    if l == r:
        return 0, u'The data are equals'
    n, m = len(l), len(r)
    if n != m:
        return -1, u'The data to compare has different sizes'
    offset = 0
    length = 0
    result = u''
    diffs = 0
    x = 0
    while x < n:  # For every char in the string
        if str(l)[x] != str(r)[x]:  # if they differs
            offset = x  # Found the beginning of a diff
            for x2 in range(offset, n):  # Start checking the size of the diff
                if str(l)[x2] != str(r)[x2]:  # loop until the diff ends
                    length += 1  # while different sum the length of the diff
                else:

                    break  # Break and account the results
            diffs += 1
            result += u'Offset: %d, Length: %d\n' % (offset, length)
            x = offset + length  # Change the first loop to continue from the last position of the las diff
            length = 0  # Reset length for next interaction
        else:  # If equal, move offset
            offset += 1
        x += 1
    return diffs, result


# AUXILIARY METHODS
def get_json(d, data=None):
    """
    Parse and DiffModel onejct to JSON
    :param d: The DiffModel object
    :param data: The data when needed (just for ease the GET answer)
    :return:
    """
    m = {
        'id': d.id,
        'side': d.side,
        'uri': 'http://localhost/v1/diff/%d/%s' % (d.id, d.side)
    }
    if data:
        m['data'] = data
    return m


def diff_json(id, code, message):
    j = {
        'id': id,
        'result': {
            'code': code,
            'message': message
        },
        'uri': 'http://localhost/v1/diff/%d' % id
    }
    return j


def side_not_found(id):
    msg = 'It is missing one side'
    return json.dumps((diff_json(id, -2, msg)))


def validate_endpoint_uri(side):
    """
    Check if the call was made to the known side diff APIs
    """
    if str(side) not in [u'left', u'right']:
        abort(404)


# APIs
class DiffApi(Resource):
    """
    The diff API
    """
    def get(self, id):
        """
        Return the diff between the datas stored fot the specified id
        :param id: The data id
        """
        left = DiffModel.query.filter_by(id=id, side='left').first()
        right = DiffModel.query.filter_by(id=id, side='right').first()
        if not left or not right:
            j = side_not_found(id)
            return make_response(j, 404)
        result = diff(left.data, right.data)
        r = diff_json(id, result[0], result[1])
        return make_response(json.dumps(r), 200)


class DiffSidesApi(Resource):
    """
    This is the API that received the left and right Base64 content and stores in the database.
    """
    # Helpful constants
    LEFT = u'left'
    RIGHT = u'right'

    def __init__(self):
        """
        Creates a argument parser to ease the request data extraction
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=str, required=True,
                                   help='No data received', location='json')
        super(DiffSidesApi, self).__init__()

    def get(self, id, side):
        """
        Answer GET requests
        Validate the data and return the diff side data
        """
        validate_endpoint_uri(side)
        d = DiffModel.query.filter_by(id=id, side=unicode(side)).first()
        if not d:
            r = {
                'message': 'Invalid ID.'
            }
            return make_response(jsonify(r), 404)
        r = get_json(d, data=d.data)
        return make_response(jsonify(r), 200)

    def post(self, id, side):
        """
        Answer POST requests
        Receives a diff side data and stores in the database after validation
        """
        validate_endpoint_uri(side)
        args = self.reqparse.parse_args()
        d = DiffModel(id, side, args['data'])
        db.session.add(d)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            error = {
                'message': 'This ID is already in use. To update make a PUT request.'
            }
            return make_response(jsonify(error), 409)
        m = get_json(d)
        return make_response(jsonify(m), 201)

    def put(self, id, side):
        """
        Answer PUT requests
        Validate the data and update them in the database
        """
        validate_endpoint_uri(side)
        args = self.reqparse.parse_args()
        d = DiffModel.query.filter_by(id=id, side=side).first()
        if not d:
            abort(404)
        d.data = args['data']
        try:
            db.session.commit()
        except Exception as e:
            error = {
                'message': e.message
            }
            return make_response(jsonify(error), 401)
        r = get_json(d)
        return make_response(jsonify(r), 200)

    def delete(self, id, side):
        """
        Answer the DELETE requests
        Validate the data and delete the diff side data in the database
        """
        validate_endpoint_uri(side)
        d = DiffModel.query.filter_by(id=id, side=side).first()
        if not d:
            abort(404)
        db.session.delete(d)
        try:
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({'message': e.message}), 401)
        ret = {
            'message': 'Diff deleted.'
        }
        return make_response(jsonify(ret), 204)


""" Register the APIs """
api.add_resource(DiffApi, '/v1/diff/<int:id>', endpoint='diff')
# Instead of having two different endpoints for the same purpose, it is easier to transform the side in a parameter
# The parameter is treated inside method calls
api.add_resource(DiffSidesApi, '/v1/diff/<int:id>/<string:side>', endpoint='side')
