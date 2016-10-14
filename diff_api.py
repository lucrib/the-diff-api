from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()


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


database = [
    {
        'data': u'',
        'id': 1
    },
    {
        'data': fields.String,
        'id': 2
    },
    {
        'data': fields.String,
        'id': 3
    }
]

to_be_diff = {
    'data': fields.String,
    'uri': fields.Url('diff')
}


class DiffApi(Resource):

    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    def get(self, id, side):
        v = 'Received a call for %s with id = %d' % (side, id)
        return {'return': v}


class DiffLeftApi(DiffApi):

    def get(self, id):
        return super(DiffLeftApi, self).get(id, self.LEFT)


class DiffRightApi(DiffApi):

    def get(self, id):
        return super(DiffRightApi, self).get(id, self.LEFT)


api.add_resource(DiffLeftApi, '/v1/diff/<int:id>/left', endpoint='left')
api.add_resource(DiffRightApi, '/v1/diff/<int:id>/right', endpoint='right')

if __name__ == '__main__':
    app.run(debug=True)
