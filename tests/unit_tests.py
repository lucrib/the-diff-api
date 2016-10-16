import base64
import unittest
from app import app
from app.rest_api import diff


class DiffLogicTest(unittest.TestCase):

    def test_equal_values(self):
        a = b'THIS IS EQUAL'
        b = b'THIS IS EQUAL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == 0
        assert diff_res[1] == u'The data are equals'

    def test_one_diff_session(self):
        a = b'NOT EQUAL'
        b = b'YES EQUAL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == 1
        assert diff_res[1] == u'Offset: 0, Length: 3\n'

    def test_two_diff_session(self):
        a = b'NOT EQUAL, BUT GOOD'
        b = b'YES EQUAL, BUT WELL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == 2
        assert u'Offset: 0, Length: 3\n' in diff_res[1]
        assert u'Offset: 15, Length: 4\n' in diff_res[1]

    def test_entire_diff(self):
        a = b'ENTIRELYDIFFERENT'
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == 1
        assert u'Offset: 0, Length: 17\n' in diff_res[1]

    def test_diff_not_equal_size_left(self):
        a = b'ENTIRELYDIFFERENTAAA'
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == -1
        assert diff_res[1] == u'The data to compare has different sizes'

    def test_diff_not_equal_size_right(self):
        a = b'ENTIRELYDIFFERENT'
        b = b'DIFFERENTLYENTIREAAA'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == -1
        assert diff_res[1] == u'The data to compare has different sizes'

    def test_diff_none_left(self):
        a = b''
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == -1
        assert diff_res[1] == u'The data to compare has different sizes'

    def test_diff_none_right(self):
        a = b'ENTIRELYDIFFERENT'
        b = b''
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert diff_res[0] == -1
        assert diff_res[1] == u'The data to compare has different sizes'


class IntegrationTest(unittest.TestCase):
    tester = app.test_client(use_cookies=False)

    def test(self):
        res = self.tester.get('/v1/diff/1')
        print res.default_mime_type


if __name__ == '__main__':
    unittest.main()