import unittest
import base64
import diff_api


class DiffLogicTest(unittest.TestCase):

    def test_diff_equal_values(self):
        a = b'THIS IS EQUAL'
        b = b'THIS IS EQUAL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff_api.diff(left, right)
        assert diff_res[0] == 0
        assert diff_res[1] == u'The data are equals'

    def test_one_diff_session(self):
        a = b'NOT EQUAL'
        b = b'YES EQUAL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff_api.diff(left, right)
        assert diff_res[0] == 1
        assert diff_res[1] == u'Offset: 0, Length: 3\n'

    def test_two_diff_session(self):
        a = b'NOT EQUAL, BUT GOOD'
        b = b'YES EQUAL, BUT WELL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff_api.diff(left, right)
        assert diff_res[0] == 2
        assert u'Offset: 0, Length: 3\n' in diff_res[1]
        assert u'Offset: 15, Length: 4\n' in diff_res[1]

    def test_entire_diff(self):
        a = b'ENTIRELYDIFFERENT'
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff_api.diff(left, right)
        assert diff_res[0] == 1
        assert u'Offset: 0, Length: 17\n' in diff_res[1]
