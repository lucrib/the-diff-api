import unittest
import json
import base64
from hamcrest import *
from app import app as diff_api


class BaseTest(unittest.TestCase):
    content_type = "application/json"

    def setUp(self):
        diff_api.config['TESTING'] = True
        self.app = diff_api.test_client()

    def tearDown(self):
        diff_api.clear_db()

    # Auxiliar methods

    def get_invalid_id_side(self, side):
        ep = '/v1/diff/%d/%s' % (99, side)
        # GET
        rv = self.app.get(ep)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(404))
        assert_that(rv.content_type, has_string('application/json'))
        r_data = json.loads(rv.data)
        assert_that(r_data, has_key('message'))
        assert_that(r_data['message'], contains_string('Invalid ID.'))

    def get_invalid_id_type(self, side):
        ep = '/v1/diff/%s/%s' % ('invalid', side)
        # GET
        rv = self.app.get(ep)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(404))
        assert_that(rv.content_type, has_string('text/html'))
        assert_that(rv.data, contains_string("<title>404 Not Found</title>"))
        assert_that(rv.data, contains_string("<h1>Not Found</h1>"))

    def post_get_put_delete_diff_side(self, side):
        id = 1
        data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        ed = self.expected_diff_side_data(id, side)
        ep = '/v1/diff/%d/%s' % (id, side)
        # POST
        rv = self.app.post(ep, data=json.dumps(data), content_type=self.content_type)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(201))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(json.loads(rv.data), equal_to(ed))
        # GET
        ed = self.expected_diff_side_data(id, side, data=data)
        rv = self.app.get(ep)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(200))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(json.loads(rv.data), equal_to(ed))
        # PUT
        data = {
            "data": base64.b64encode(b"RIBEIRO LUCAS")
        }
        ed = self.expected_diff_side_data(id, side)
        rv = self.app.put(ep, data=json.dumps(data), content_type=self.content_type)
        assert_that(rv.status_code, equal_to(200))
        assert_that(json.loads(rv.data), equal_to(ed))
        assert_that(rv.content_type, has_string('application/json'))
        # DELETE
        rv = self.app.delete(ep, data=json.dumps(data), content_type=self.content_type)
        assert_that(rv.status_code, equal_to(204))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(rv.data, equal_to(u''))

    def expected_diff_side_data(self, id, side, data=None):
        expected_data = {
            u'id': id,
            u'side': unicode(side),
            u'uri': unicode('http://localhost/v1/diff/%d/%s' % (id, side)),
        }
        if data:
            expected_data[u'data'] = unicode(data['data'])
        return expected_data

    def expected_diff_data(self, id, side, res_code, res_message):
        ed = {
            u'result': {
                u'message': res_message,
                u'code': res_code
            },
            u'uri': u'http://localhost/v1/diff/5'
        }
        return ed


class TestDiffSideAPI(BaseTest):

    def test_post_get_put_delete_diff_left(self):
        self.post_get_put_delete_diff_side('left')

    def test_post_get_put_delete_diff_right(self):
        self.post_get_put_delete_diff_side('right')

    def test_get_invalid_id_left(self):
        self.get_invalid_id_side('left')

    def test_get_invalid_id_right(self):
        self.get_invalid_id_side('right')

    def test_get_invalid_id_type_left(self):
        self.get_invalid_id_type('left')

    def test_get_invalid_id_type_right(self):
        self.get_invalid_id_type('right')

    def test_get_invalid_side(self):
        ep = '/v1/diff/%d/%s' % (1, 'invalid')
        # GET
        rv = self.app.get(ep)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(404))
        assert_that(rv.content_type, has_string('application/json'))
        r_data = json.loads(rv.data)
        assert_that(r_data, has_key('message'))
        assert_that(r_data['message'], contains_string('The requested URL was not found on the server.'))


class TestDiffAPI(BaseTest):

    EQ_DATA = u'The data are equals'
    EQ_DATA_CODE = 0
    NOT_EQ_DATA = u'The data to compare has different sizes'
    NOT_EQ_DATA_CODE = -1
    ERROR_CODE = -2

    def test_diff_equal_values(self):
        side_data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        rv = self.app.post('/v1/diff/5/left', data=json.dumps(side_data), content_type=self.content_type)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.post('/v1/diff/5/right', data=json.dumps(side_data), content_type=self.content_type)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.get('/v1/diff/5')
        ed = self.expected_diff_data(5, 'left', self.EQ_DATA_CODE, self.EQ_DATA)
        r_data = json.loads(rv.data)
        assert_that(r_data, equal_to(ed))


if __name__ == '__main__':
    unittest.main()
