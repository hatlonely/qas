#!/usr/bin/env python3


from .expect import *
import unittest


class TestExpectVal(unittest.TestCase):
    def test_expect_val(self):
        self.assertTrue(expect_val("val % 2 == 1", val=1))
        self.assertTrue(expect_val("val.endswith('v3')", val="eeb848f8611a4ff980d2e56a2760b4fcv3"))


class TestExpectObj(unittest.TestCase):
    def test_expect_dict_equal(self):
        res = expect({
            "status": 200,
            "json": {
                "hex": "533f6046eb7f610e",
                "num": "5998619086395760910",
            }
        }, {
            "status": 200,
            "json": {
                "hex": "533f6046eb7f610e",
                "num": "5998619086395760910",
            }
        })
        self.assertTrue(res)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], ExpectResult(is_pass=True, message="OK", node="status", val=200, expect=200))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="json.hex", val="533f6046eb7f610e", expect="533f6046eb7f610e"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="json.num", val="5998619086395760910", expect="5998619086395760910"))

    def test_expect_dict_not_equal(self):
        res = expect({
            "status": 200,
            "json": {
                "hex": "533f6046eb7f610e",
                "num": "5998619086395760910",
            }
        }, {
            "status": 201,
            "json": {
                "hex": "533f6046eb7f610e",
                "num": "xx",
            }
        })
        self.assertTrue(res)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], ExpectResult(is_pass=False, message="NotEqual", node="status", val=200, expect=201))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="json.hex", val="533f6046eb7f610e", expect="533f6046eb7f610e"))
        self.assertEqual(res[2], ExpectResult(is_pass=False, message="NotEqual", node="json.num", val="5998619086395760910", expect="xx"))

    def test_expect_list_equal(self):
        res = expect({
            "status": 200,
            "json": [{
                "hex": "111",
                "num": "222",
            }, {
                "hex": "333",
                "num": "444",
            }]
        }, {
            "status": 200,
            "json": [{
                "hex": "111",
                "num": "222",
            }, {
                "hex": "333",
                "num": "444",
            }]
        })
        self.assertTrue(res)
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0], ExpectResult(is_pass=True, message="OK", node="status", val=200, expect=200))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="json.0.hex", val="111", expect="111"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="json.0.num", val="222", expect="222"))
        self.assertEqual(res[3], ExpectResult(is_pass=True, message="OK", node="json.1.hex", val="333", expect="333"))
        self.assertEqual(res[4], ExpectResult(is_pass=True, message="OK", node="json.1.num", val="444", expect="444"))

    def test_expect_list_not_equal(self):
        res = expect({
            "status": 200,
            "json": [{
                "hex": "111",
                "num": "222",
            }, {
                "hex": "333",
                "num": "444",
            }]
        }, {
            "status": 201,
            "json": [{
                "hex": "123",
                "num": "222",
            }, {
                "hex": "333",
                "num": "456",
            }]
        })
        self.assertTrue(res)
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0], ExpectResult(is_pass=False, message="NotEqual", node="status", val=200, expect=201))
        self.assertEqual(res[1], ExpectResult(is_pass=False, message="NotEqual", node="json.0.hex", val="111", expect="123"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="json.0.num", val="222", expect="222"))
        self.assertEqual(res[3], ExpectResult(is_pass=True, message="OK", node="json.1.hex", val="333", expect="333"))
        self.assertEqual(res[4], ExpectResult(is_pass=False, message="NotEqual", node="json.1.num", val="444", expect="456"))

    def test_expect_list_equal_2(self):
        res = expect([
            {
                "hex": "111",
                "num": "222",
            }, {
                "hex": "333",
                "num": "444",
            }], [{
                "hex": "111",
                "num": "222",
            }, {
                "hex": "333",
                "num": "444",
            }
        ])
        self.assertTrue(res)
        self.assertEqual(len(res), 4)
        self.assertEqual(res[0], ExpectResult(is_pass=True, message="OK", node="0.hex", val="111", expect="111"))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="0.num", val="222", expect="222"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="1.hex", val="333", expect="333"))
        self.assertEqual(res[3], ExpectResult(is_pass=True, message="OK", node="1.num", val="444", expect="444"))

    def test_expect_list_not_equal_2(self):
        res = expect([
            {
                "hex": "111",
                "num": "222",
            }, {
                "hex": "333",
                "num": "444",
            }], [{
                "hex": "123",
                "num": "222",
            }, {
                "hex": "333",
                "num": "456",
            }
        ])
        self.assertTrue(res)
        self.assertEqual(len(res), 4)
        self.assertEqual(res[0], ExpectResult(is_pass=False, message="NotEqual", node="0.hex", val="111", expect="123"))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="0.num", val="222", expect="222"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="1.hex", val="333", expect="333"))
        self.assertEqual(res[3], ExpectResult(is_pass=False, message="NotEqual", node="1.num", val="444", expect="456"))


if __name__ == '__main__':
    unittest.main()
