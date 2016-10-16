import unittest
import json
import ast
from hamcrest import *
from app import app as diff_api


class BaseTest(unittest.TestCase):

    def setUp(self):
        diff_api.config['TESTING'] = True
        self.app = diff_api.test_client()

    def call(self, method, ep, **kwargs):
        if method == 'GET':
            return self.app.get(ep, **kwargs)
        elif method == 'POST':
            return self.app.post(ep, **kwargs)
        elif method == 'PUT':
            return self.app.put(ep, **kwargs)
        elif method == 'DELETE':
            return self.app.delete(ep, **kwargs)
        return None

    def call_diff(self, method, id, **kwarg):
        ep = '/v1/diff/%d' % id
        return self.call(method, ep, **kwarg)

    def call_diff_side(self, method, id, side, **kwarg):
        ep = '/v1/diff/%d/%s' % (id, side)
        return self.call(method, ep, **kwarg)


class DiffSideTest(BaseTest):
    side = ''

    def test_get_valid_diff(self):
        # Arrange
        expected = {
            "message": {
                "id": 1,
                "side": self.side,
                "data": "LUCAS RIBEIRO"
            }
        }
        # Act
        rv = self.call_diff_side('GET', 1, self.side)
        print rv.data
        actual = ast.literal_eval(rv.data)
        print actual
        # Assert
        assert_that(actual, equal_to(expected))
        assert_that(rv.status_code, equal_to(200))

    def test_post(self):
        # Arrange
        expected = {
            "message": {
                "id": 1,
                "side": self.side,
                "data": "LUCAS RIBEIRO",
                "uri": "/v1/diff/1/%s" % self.side
            }
        }
        data = {
            "data": u"LUCAS RIBEIRO"
        }
        # Act
        rv = self.call_diff_side('POST', 2, self.side, data=json.dumps(data), content_type="application/json")
        actual = json.dumps(rv.data)
        print actual
        print expected
        # Assert
        assert_that(actual, equal_to(expected))


class LeftDiffTest(DiffSideTest):
    side = 'left'


class RightDiffTest(DiffSideTest):
    side = 'right'


class TestDiffSideAPI(BaseTest):

    def test_create_left_diff(self):
        data = {
            "data": "LUCAS RIBEIRO"
        }
        content_type = "application/json"
        rv = self.app.post('/v1/diff/1/left', data=json.dumps(data), content_type=content_type)
        # print json.loads(rv.data)
        assert_that(rv.status_code, equal_to(201))
        assert_that(rv.content_type, has_string('application/json'))

if __name__ == '__main__':
    import coverage
    cov = coverage.Coverage()
    cov.start()

    # left = DiffSideApiTest('left')
    # right = DiffSideApiTest('right')
    #
    # test_cases = [left, right]
    # s = unittest.TestSuite()
    # s.addTest(left)
    # s.addTest(right)
    # result = None
    # s.run(result)
    unittest.main()

    cov.stop()
    cov.save()
    cov.report()
    # cov.html_report()
