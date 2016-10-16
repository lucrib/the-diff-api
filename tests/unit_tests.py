import base64
import unittest

from hamcrest import *

from rest_api import diff


class DiffLogicTest(unittest.TestCase):

    def test_equal_values(self):
        a = b'THIS IS EQUAL'
        b = b'THIS IS EQUAL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(0))
        assert_that(diff_res[1], equal_to(u'The data are equals'))

    def test_one_diff_session(self):
        a = b'NOT EQUAL'
        b = b'YES EQUAL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(1))
        assert_that(diff_res[1], equal_to(u'Offset: 0, Length: 3\n'))

    def test_two_diff_session(self):
        a = b'NOT EQUAL, BUT GOOD'
        b = b'YES EQUAL, BUT WELL'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(2))
        assert_that(diff_res[1], equal_to(u'Offset: 0, Length: 3\nOffset: 15, Length: 4\n'))

    def test_entire_diff(self):
        a = b'ENTIRELYDIFFERENT'
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(1))
        assert_that(diff_res[1], equal_to(u'Offset: 0, Length: 17\n'))

    def test_diff_not_equal_size_left(self):
        a = b'ENTIRELYDIFFERENTAAA'
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(-1))
        assert_that(diff_res[1], equal_to(u'The data to compare has different sizes'))

    def test_diff_not_equal_size_right(self):
        a = b'ENTIRELYDIFFERENT'
        b = b'DIFFERENTLYENTIREAAA'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(-1))
        assert_that(diff_res[1], equal_to(u'The data to compare has different sizes'))

    def test_diff_none_left(self):
        a = b''
        b = b'DIFFERENTLYENTIRE'
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(-1))
        assert_that(diff_res[1], equal_to(u'The data to compare has different sizes'))

    def test_diff_none_right(self):
        a = b'ENTIRELYDIFFERENT'
        b = b''
        left = base64.b64encode(a)
        right = base64.b64encode(b)
        diff_res = diff(left, right)
        assert_that(diff_res[0], equal_to(-1))
        assert_that(diff_res[1], equal_to(u'The data to compare has different sizes'))


if __name__ == '__main__':
    unittest.main()
