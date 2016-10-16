import unittest
import json
import base64
from hamcrest import *
from app import app as diff_api


class TestDiffSideAPI(unittest.TestCase):

    content_type = "application/json"

    def setUp(self):
        diff_api.config['TESTING'] = True
        self.app = diff_api.test_client()

    def tearDown(self):
        diff_api.clear_db()

    def test_post_get_put_delete_diff_left(self):
        self.post_get_put_delete_diff_side('left')

    def test_post_get_put_delete_diff_right(self):
        self.post_get_put_delete_diff_side('right')

    def test_get_invalid_id_left(self):
        self.get_invalid_id_side('left')

    def test_get_invalid_id_right(self):
        self.get_invalid_id_side('right')

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

    def post_get_put_delete_diff_side(self, side):
        id = 1
        data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        ed = self.expected_data(id, side)
        ep = '/v1/diff/%d/%s' % (id, side)
        # POST
        rv = self.app.post(ep, data=json.dumps(data), content_type=self.content_type)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(201))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(json.loads(rv.data), equal_to(ed))
        # GET
        ed = self.expected_data(id, side, data=data)
        rv = self.app.get(ep)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(200))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(json.loads(rv.data), equal_to(ed))
        # PUT
        data = {
            "data": base64.b64encode(b"RIBEIRO LUCAS")
        }
        ed = self.expected_data(id, side)
        rv = self.app.put(ep, data=json.dumps(data), content_type=self.content_type)
        assert_that(rv.status_code, equal_to(200))
        assert_that(json.loads(rv.data), equal_to(ed))
        assert_that(rv.content_type, has_string('application/json'))
        # DELETE
        rv = self.app.delete(ep, data=json.dumps(data), content_type=self.content_type)
        assert_that(rv.status_code, equal_to(204))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(rv.data, equal_to(u''))

    def expected_data(self, id, side, data=None):
        expected_data = {
            u'id': id,
            u'side': unicode(side),
            u'uri': unicode('http://localhost/v1/diff/%d/%s' % (id, side)),
        }
        if data:
            expected_data[u'data'] = unicode(data['data'])
        return expected_data


if __name__ == '__main__':
    unittest.main()

