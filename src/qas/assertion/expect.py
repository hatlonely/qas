#!/usr/bin/env python3


import unittest
from dataclasses import dataclass


@dataclass
class ExpectResult:
    is_pass: bool
    message: str
    node: str
    val: any
    expect: any


@dataclass
class StepResult:
    step: str
    expect_results: list[ExpectResult]
    is_pass: bool
    succ: int
    fail: int

    def __init__(self, step=""):
        self.step = step
        self.expect_results = list[ExpectResult]()
        self.is_pass = True
        self.succ = 0
        self.fail = 0

    def summary(self):
        self.succ = sum(1 for i in self.expect_results if i.is_pass)
        self.fail = len(self.expect_results) - self.succ
        self.is_pass = self.fail == 0


@dataclass
class CaseResult:
    case: str
    step_results: list[StepResult]
    is_pass: bool

    def __init__(self, case=""):
        self.case = case
        self.step_results = list[StepResult]()
        self.is_pass = True

    def summary(self):
        for r in self.step_results:
            r.summary()
        self.is_pass = all(i.is_pass for i in self.step_results)


@dataclass
class TestResult:
    name: str
    case_results: list[CaseResult]
    is_pass: bool
    succ: int
    fail: int

    def __init__(self, name=""):
        self.name = name
        self.case_results = list[CaseResult]()
        self.is_pass = True
        self.succ = 0
        self.fail = 0

    def summary(self):
        for r in self.case_results:
            r.summary()
        self.succ = sum(1 for i in self.case_results if i.is_pass)
        self.fail = len(self.case_results) - self.succ
        self.is_pass = self.fail == 0


def expect_obj(vals, rules):
    expect_results = []
    if isinstance(rules, dict):
        expect_obj_recursive("", vals, rules, True, expect_results)
    elif isinstance(rules, list):
        expect_obj_recursive("", vals, rules, False, expect_results)
    else:
        pass
    return expect_results


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
            if isinstance(key, str) and key.startswith("$"):
                msg, ok = expect_val(root_dot_key, val, rule)
                if not ok:
                    expect_results.append(ExpectResult(is_pass=False, message=msg, node=root_dot_key, val=val, expect=rule))
                else:
                    expect_results.append(ExpectResult(is_pass=True, message="OK", node=root_dot_key, val=val, expect=rule))
            else:
                if val != rule:
                    expect_results.append(ExpectResult(is_pass=False, message="val not equal", node=root_dot_key, val=val, expect=rule))
                else:
                    expect_results.append(ExpectResult(is_pass=True, message="OK", node=root_dot_key, val=val, expect=rule))


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
        self.assertTrue(res)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], ExpectResult(is_pass=True, message="OK", node="status", val=200, expect=200))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="json.hex", val="533f6046eb7f610e", expect="533f6046eb7f610e"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="json.num", val="5998619086395760910", expect="5998619086395760910"))

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
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], ExpectResult(is_pass=False, message="val not equal", node="status", val=200, expect=201))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="json.hex", val="533f6046eb7f610e", expect="533f6046eb7f610e"))
        self.assertEqual(res[2], ExpectResult(is_pass=False, message="val not equal", node="json.num", val="5998619086395760910", expect="xx"))

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
        self.assertTrue(res)
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0], ExpectResult(is_pass=True, message="OK", node="status", val=200, expect=200))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="json.0.hex", val="111", expect="111"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="json.0.num", val="222", expect="222"))
        self.assertEqual(res[3], ExpectResult(is_pass=True, message="OK", node="json.1.hex", val="333", expect="333"))
        self.assertEqual(res[4], ExpectResult(is_pass=True, message="OK", node="json.1.num", val="444", expect="444"))

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
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0], ExpectResult(is_pass=False, message="val not equal", node="status", val=200, expect=201))
        self.assertEqual(res[1], ExpectResult(is_pass=False, message="val not equal", node="json.0.hex", val="111", expect="123"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="json.0.num", val="222", expect="222"))
        self.assertEqual(res[3], ExpectResult(is_pass=True, message="OK", node="json.1.hex", val="333", expect="333"))
        self.assertEqual(res[4], ExpectResult(is_pass=False, message="val not equal", node="json.1.num", val="444", expect="456"))

    def test_expect_obj_list_equal_2(self):
        res = expect_obj([
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

    def test_expect_obj_list_not_equal_2(self):
        res = expect_obj([
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
        self.assertEqual(res[0], ExpectResult(is_pass=False, message="val not equal", node="0.hex", val="111", expect="123"))
        self.assertEqual(res[1], ExpectResult(is_pass=True, message="OK", node="0.num", val="222", expect="222"))
        self.assertEqual(res[2], ExpectResult(is_pass=True, message="OK", node="1.hex", val="333", expect="333"))
        self.assertEqual(res[3], ExpectResult(is_pass=False, message="val not equal", node="1.num", val="444", expect="456"))


if __name__ == '__main__':
    unittest.main()

