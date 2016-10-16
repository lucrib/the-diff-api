import base64
import json
from flask import jsonify, abort, make_response
from flask_restful import Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from app import db
from app.models import DiffModel
import sqlalchemy.exc

auth = HTTPBasicAuth()


def diff(left, right):
    try:
        l = base64.b64decode(left)
        r = base64.b64decode(right)
    except Exception as e:
        return -3, unicode(e.message)
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


class DiffApi(Resource):
    def get(self, id):
        left = DiffModel.query.filter_by(id=id, side='left').first()
        right = DiffModel.query.filter_by(id=id, side='right').first()
        if not left or not right:
            j = self.side_not_found(id)
            return make_response(j, 404)
        result = diff(left.data, right.data)
        r = self.diff_json(id, result[0], result[1])
        return make_response(json.dumps(r), 200)

    def diff_json(self, id, code, message):
        json = {
            'id': id,
            'result': {
                'code': code,
                'message': message
            },
            'uri': 'http://localhost/v1/diff/%d' % id
        }
        return json

    def side_not_found(self, id):
        msg = 'It is missing one side'
        return json.dumps((self.diff_json(id, -2, msg)))

    def post(self):
        abort(404)

    def put(self):
        abort(404)

    def delete(self):
        abort(404)


class DiffSidesApi(Resource):
    """ This is the API that received the left and right Base64 content and stores that in the database."""
    # Side constants
    LEFT = u'left'
    RIGHT = u'right'

    # The JSON model

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=str, required=True,
                                   help='No data received', location='json')
        super(DiffSidesApi, self).__init__()

    def get(self, id, side):
        self.validate_endpoint_uri(side)
        d = DiffModel.query.filter_by(id=id, side=unicode(side)).first()
        if not d:
            r = {
                'message': 'Invalid ID.'
            }
            return make_response(jsonify(r), 404)
        r = get_json(d, data=d.data)
        return make_response(jsonify(r), 200)

    def post(self, id, side):
        """ Receives a diff side data and stores in the database"""
        self.validate_endpoint_uri(side)
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
        self.validate_endpoint_uri(side)
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
        self.validate_endpoint_uri(side)
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

    def validate_endpoint_uri(self, side):
        if str(side) not in [u'left', u'right']:
            abort(404)


def get_json(d, data=None):
    m = {
        'id': d.id,
        'side': d.side,
        'uri': 'http://localhost/v1/diff/%d/%s' % (d.id, d.side)
    }
    if data:
        m['data'] = data
    return m
