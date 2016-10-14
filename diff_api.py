from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
import base64


app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()

DATABASE = [
    # Equal Data
    {'id': 1, 'data': 'TFVDQVMgUklCRUlSTw==', 'side': 'left'},
    {'id': 1, 'data': 'TFVDQVMgUklCRUlSTw==', 'side': 'right'},
    # Different Size
    {'id': 2, 'data': 'TFVDQVMgUklCRUlSTw==', 'side': 'left'},
    {'id': 2, 'data': 'TFVDQVMgUklCRUlSTw==X', 'side': 'right'},
    # Missing right
    {'id': 3, 'data': 'TFVDQVMgUklCRUlSTw==', 'side': 'left'},
    {'id': 3, 'data': '', 'side': 'right'},
    # Missing left
    {'id': 4, 'data': '', 'side': 'left'},
    {'id': 4, 'data': 'TFVDQVMgUklCRUlSTw==', 'side': 'right'},
    # Differs
    {'id': 5, 'data': 'TFVDQVMgUklCRUlSTw==A', 'side': 'left'},
    {'id': 5, 'data': 'TFVDQVMgUklCRUlSTw==B', 'side': 'right'},
]


def diff(left, right):
    l = base64.b64decode(left)
    r = base64.b64decode(right)
    print '{} => {}'.format(l, r)
    print '{}\n{}'.format(l, r)
    n, m = len(l), len(r)
    if n != m:
        return -1
    offset = 0
    lenght = 0
    result = u''
    last = False
    x = 0
    while x < n:  # For every char in the string
        if str(l)[x] != str(r)[x]:  # if they differs
            offset = x  # Found a offset
            for x2 in range(offset, n):  # Start checking the size of the diff
                if str(l)[x2] != str(r)[x2]:
                    lenght += 1
                else:
                    break
            result += 'Offset: %d, Size: %d\n' % (offset, lenght)
            x = offset + lenght
            lenght = 0
        else:
            offset += 1
        x+=1
    print result
    return result


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
    def __init__(self):
        pass

    def get(self, id):
        return jsonify(
            {
                'response': {
                    'uri': '/v1/diff/%d' % id
                }
            }
        )


class DiffSidesApi(Resource):
    """ This is the API that received the left and right Base64 content and stores that in the database.
    """
    # Definition of the sides
    LEFT = u'left'
    RIGHT = u'right'
    # The JSON model
    diff_data_fields = {
        'data': fields.String,
        'side': fields.String,
        'uri': fields.Url('side')
    }  # id is automatic handled

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=str, required=True,
                                   help='No data received', location='json')
        super(DiffSidesApi, self).__init__()

    def get(self, id, side):
        self.validate_endpoint_uri(side)
        r = [data for data in DATABASE if (data['id'] == id and data['side'] == side)]
        if not r:
            abort(404)
        # return marshal(r[0], self.diff_data_fields)
        return jsonify(r)

    # TODO Add a validaiton to do not overwrite existing data
    def post(self, id, side):
        self.validate_endpoint_uri(side)
        args = self.reqparse.parse_args()
        data = self.sava_data(id, side, args)
        return marshal(data, self.diff_data_fields), 201

    # FIXME IT is saving a new object instead of updating
    def put(self, id, side):
        self.validate_endpoint_uri(side)
        data = [data for data in DATABASE if (data['id'] == id and data['side'] == side)]
        if data:
            args = self.reqparse.parse_args()
            new_data = self.sava_data(id, side, args)
            return marshal(new_data, self.diff_data_fields)
        abort(404)

    def delete(self, id, side):
        self.validate_endpoint_uri(side)
        for data in DATABASE:
            if data['id'] == id and data['side'] == side:
                i = DATABASE.index(data)
                DATABASE.pop(i)
                return make_response(jsonify({'message': 'deleted'}), 200)
        abort(404)

    def sava_data(self, id, side, args):
        data = {
            'id': id,
            'data': args['data'],
            'side': side
        }
        DATABASE.append(data)
        return data

    def validate_endpoint_uri(self, side):
        if str(side) not in [u'left', u'right']:
            abort(404)


api.add_resource(DiffApi, '/v1/diff/<int:id>', endpoint='diff')
# Instead of having two different endpoints for the same purpose, it easier to transform the side in a parameter
# The parameter is treated inside method calls
api.add_resource(DiffSidesApi, '/v1/diff/<int:id>/<string:side>', endpoint='side')

if __name__ == '__main__':
    app.run(debug=True)
