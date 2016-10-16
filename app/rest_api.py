import base64
import json
from flask import jsonify, abort, make_response, url_for
from flask_restful import Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from app import db
from app.models import DiffModel
import sqlalchemy.exc

auth = HTTPBasicAuth()


def diff(left, right):
    l = base64.b64decode(left)
    r = base64.b64decode(right)
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


@auth.get_password
def get_password(username):
    if username == 'tester':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


class DiffApi(Resource):
    def get(self, id):
        left = DiffModel.query.filter_by(id=id, side='left').first()
        right = DiffModel.query.filter_by(id=id, side='right').first()
        if not left.data or not right.data:
            abort(422)
        left = bytearray(unicode(left))
        right = bytearray(unicode(right))
        result = diff(left, right)
        return jsonify(
            {
                'result': {
                    'code': result[0],
                    'message': result[1]
                },
                'uri': '/v1/diff/%d' % id
            }
        )

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
