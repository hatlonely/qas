#!/usr/bin/env python3


import unittest
from dataclasses import dataclass


def expect_obj(vals, rules):
    expect_results = []
    expect_obj_recursive("", vals, rules, True, expect_results)
    return expect_results


@dataclass
class ExpectResult:
    isPass: bool
    message: str
    node: str
    val: any
    expect: any


def expect_obj_recursive(root: str, vals, rules, is_dict: bool, expect_results: list):
    if is_dict:
        to_enumerate = rules.items()
    else:
        to_enumerate = enumerate(rules)
    for key, rule in to_enumerate:
        val = vals[key]
        root_dot_key = "{}.{}".format(root, key).lstrip(".")
        if isinstance(rule, dict):
            expect_obj_recursive(root_dot_key, val, rule, True, expect_results)
        elif isinstance(rule, list):
            expect_obj_recursive(root_dot_key, val, rule, False, expect_results)
        else:
            if key is str and key.startswith("$"):
                msg, ok = expect_val(root_dot_key, val, rule)
                if not ok:
                    expect_results.append(ExpectResult(
                        isPass=False,
                        message=msg,
                        node=root_dot_key,
                        val=val,
                        expect=rule,
                    ))
                    return root_dot_key, msg, False
            else:
                if val != rule:
                    expect_results.append(ExpectResult(
                        isPass=False,
                        message="val not equal",
                        node=root_dot_key,
                        val=val,
                        expect=rule,
                    ))


def expect_val(root, val, rule):
    return True


class TestExpectObj(unittest.TestCase):
    def test_expect_obj_dict_equal(self):
        res = expect_obj({
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
        self.assertFalse(res)

    def test_expect_obj_dict_not_equal(self):
        res = expect_obj({
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
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], ExpectResult(
            isPass=False,
            message="val not equal",
            node="status",
            val=200,
            expect=201,
        ))
        self.assertEqual(res[1], ExpectResult(
            isPass=False,
            message="val not equal",
            node="json.num",
            val="5998619086395760910",
            expect="xx",
        ))

    def test_expect_obj_list_equal(self):
        res = expect_obj({
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
        self.assertFalse(res)

    def test_expect_obj_list_not_equal(self):
        res = expect_obj({
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
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], ExpectResult(
            isPass=False,
            message="val not equal",
            node="status",
            val=200,
            expect=201,
        ))
        self.assertEqual(res[1], ExpectResult(
            isPass=False,
            message="val not equal",
            node="json.0.hex",
            val="111",
            expect="123",
        ))
        self.assertEqual(res[2], ExpectResult(
            isPass=False,
            message="val not equal",
            node="json.1.num",
            val="444",
            expect="456",
        ))


if __name__ == '__main__':
    unittest.main()

