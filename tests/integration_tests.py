import base64
import json
import unittest
from rest_api import app as diff_api
from rest_api import db
from hamcrest import *


"""
This file contains the integration tests for both APIs.
There is a lot more tests tha could be writen here considering the actual implementation, but, did not have time. :'(
"""


# TODO Create a test database before testing
class BaseTest(unittest.TestCase):
    """
    This is a base class containing some tests skeletons and auxiliary methods and constants
    """
    # HELPFUL CONSTANTS
    APP_JSON = "application/json"
    ERROR_CODE = -3
    MISSING_SIDE_CODE = -2
    NOT_EQ_DATA_CODE = -1
    EQ_DATA_CODE = 0
    EQ_DATA_MESSAGE = u'The data are equals'
    NOT_EQ_DATA = u'The data to compare has different sizes'
    MISSING_SIDE_MSG = u'It is missing one side'

    def setUp(self):
        """
        Create a test context for the api to be tested (in this case all the APIs)
        """
        diff_api.config['TESTING'] = True
        self.app = diff_api.test_client()
        # Recreate all the tables
        db.create_all()

    def tearDown(self):
        """Clean things created inside the tests"""
        # Clean the database
        db.drop_all()

    # TEST SKELETONS

    def get_invalid_id_side(self, side):
        """
        Test skeleton to test a call for a invalid ID i the side API
        :param side: The side API to be called
        :type side: str
        """
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
        """
        Test skeleton call passing a invalid id type
        :param side: The side API to be called
        :type side: str
        """
        ep = '/v1/diff/%s/%s' % ('invalid', side)
        # GET
        rv = self.app.get(ep)
        assert_that(rv, not_none())
        assert_that(rv.status_code, equal_to(404))
        assert_that(rv.content_type, has_string('text/html'))
        assert_that(rv.data, contains_string("<title>404 Not Found</title>"))
        assert_that(rv.data, contains_string("<h1>Not Found</h1>"))

    # TODO Split up this test in small ones with no data dependency
    def post_get_put_delete_diff_side(self, side):
        """
        Test skeleton to CREATE, UPDATE, GET/SELECT and DELETE a diff data
        :param side: The side to be called
        :type side: str
        """
        id = 1
        data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        ed = self.expected_diff_side_data(id, side)
        ep = '/v1/diff/%d/%s' % (id, side)
        # POST
        rv = self.app.post(ep, data=json.dumps(data), content_type=self.APP_JSON)
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
        rv = self.app.put(ep, data=json.dumps(data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(200))
        assert_that(json.loads(rv.data), equal_to(ed))
        assert_that(rv.content_type, has_string('application/json'))
        # DELETE
        rv = self.app.delete(ep, data=json.dumps(data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(204))
        assert_that(rv.content_type, has_string('application/json'))
        assert_that(rv.data, equal_to(u''))

    def missing_side_data(self, side):
        id = 5
        side_data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        rv = self.app.post('/v1/diff/%d/%s' % (id, side), data=json.dumps(side_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.get('/v1/diff/%d' % id)
        ed = self.expected_diff_data(id, self.MISSING_SIDE_CODE)
        r_data = json.loads(rv.data)
        assert_that(r_data, equal_to(ed))

    # AUXILIARY METHODS

    def expected_diff_side_data(self, id, side, data=None):
        """
        Create a dictionery to be used to compare with the serve JSON answer for 'diff side data'
        :param id: The id of the data
        :param side: The side API
        :param data: The data
        :return: A dictionery that represents the JSON object of a diff side data
        :type id: int
        :type side: str
        :type data: object
        :rtype: dict
        """
        expected_data = {
            u'id': id,
            u'side': unicode(side),
            u'uri': unicode('http://localhost/v1/diff/%d/%s' % (id, side)),
        }
        if data:
            expected_data[u'data'] = unicode(data['data'])
        return expected_data

    def expected_diff_data(self, id, res_code=None, res_message=None):
        """
        Create a dictionery to be used to compare with the serve JSON answer for diff data
        :param id: The id
        :param res_code: The expected return code
        :param res_message: The expected message
        :return: A dict based on diff api data
        """
        if res_code == self.EQ_DATA_CODE:
            res_message = self.EQ_DATA_MESSAGE
        elif res_code == self.NOT_EQ_DATA_CODE:
            res_message = self.NOT_EQ_DATA
        elif res_code == self.MISSING_SIDE_CODE:
            res_message = self.MISSING_SIDE_MSG
        ed = {
            u'id': id,
            u'result': {
                u'message': res_message,
                u'code': res_code
            },
            u'uri': u'http://localhost/v1/diff/%d' % id
        }
        return ed


class TestDiffSideAPI(BaseTest):
    """
    The Test class with test for diff side api
    """
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
        """
        Test a call to a invalid side
        """
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
    """
    Test the Diff API
    """

    def test_equal_values(self):
        id = 5
        side_data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        rv = self.app.post('/v1/diff/%d/left' % id, data=json.dumps(side_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.post('/v1/diff/%d/right' % id, data=json.dumps(side_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.get('/v1/diff/%d' % id)
        ed = self.expected_diff_data(id, self.EQ_DATA_CODE)
        r_data = json.loads(rv.data)
        assert_that(r_data, equal_to(ed))

    def test_missing_left_data(self):
        self.missing_side_data('left')

    def test_missing_right_data(self):
        self.missing_side_data('right')

    def test_diff_middle_of_data(self):
        id = 50
        left_data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        right_data = {
            "data": base64.b64encode(b'LUCAS_RIBEIRO')
        }
        rv = self.app.post('/v1/diff/%d/left' % id, data=json.dumps(left_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.post('/v1/diff/%d/right' % id, data=json.dumps(right_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.get('/v1/diff/%d' % id)
        ed = self.expected_diff_data(id, 1, u'Offset: 5, Length: 1\n')
        r_data = json.loads(rv.data)
        assert_that(r_data, equal_to(ed))

    def test_diff_beginng_of_data(self):
        id = 50
        left_data = {
            "data": base64.b64encode(b'XXXAS RIBEIRO')
        }
        right_data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        rv = self.app.post('/v1/diff/%d/left' % id, data=json.dumps(left_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.post('/v1/diff/%d/right' % id, data=json.dumps(right_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.get('/v1/diff/%d' % id)
        ed = self.expected_diff_data(id, 1, u'Offset: 0, Length: 3\n')
        r_data = json.loads(rv.data)
        assert_that(r_data, equal_to(ed))

    def test_diff_ending_of_data(self):
        id = 50
        left_data = {
            "data": base64.b64encode(b'LUCAS RIBEXXX')
        }
        right_data = {
            "data": base64.b64encode(b'LUCAS RIBEIRO')
        }
        rv = self.app.post('/v1/diff/%d/left' % id, data=json.dumps(left_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.post('/v1/diff/%d/right' % id, data=json.dumps(right_data), content_type=self.APP_JSON)
        assert_that(rv.status_code, equal_to(201))
        rv = self.app.get('/v1/diff/%d' % id)
        ed = self.expected_diff_data(id, 1, u'Offset: 10, Length: 3\n')
        r_data = json.loads(rv.data)
        assert_that(r_data, equal_to(ed))

if __name__ == '__main__':
    unittest.main()
