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
        'data': u'AAABBB',
        'id': 1,
        'side': 'left'
    },
    {
        'data': u'AAAAAA',
        'id': 2,
        'side': 'left'

    },
    {
        'data': u'BBBBBB',
        'id': 3,
        'side': 'left'
    }
]

to_be_diff = {
    'data': fields.String,
    'uri': fields.Url('diff')
}


class DiffApi(Resource):

    LEFT = 'left'
    RIGHT = 'right'

    def get(self, id, side):
        data = [d for d in database if (d['id'] == id and d['side'] == side)]
        if not data:
            abort(404)
        return jsonify({'return': d})


class DiffLeftApi(DiffApi):

    def get(self, id):
        response = super(DiffLeftApi, self).get(id, self.LEFT)
        return response


class DiffRightApi(DiffApi):

    def get(self, id):
        response = super(DiffRightApi, self).get(id, self.RIGHT)
        return response


api.add_resource(DiffLeftApi, '/v1/diff/<int:id>/left', endpoint='left')
api.add_resource(DiffRightApi, '/v1/diff/<int:id>/right', endpoint='right')

if __name__ == '__main__':
    app.run(debug=True)
