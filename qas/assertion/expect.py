#!/usr/bin/env python3


from dataclasses import dataclass
from datetime import datetime, timezone
from dateutil import parser


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
        root_dot_key = "{}.{}".format(root, key).lstrip(".")
        if isinstance(rule, dict):
            expect_obj_recursive(root_dot_key, vals[key], rule, True, expect_results)
        elif isinstance(rule, list):
            expect_obj_recursive(root_dot_key, vals[key], rule, False, expect_results)
        else:
            if isinstance(key, str) and key.startswith("#"):
                val = vals[key[1:]]
                ok = expect_val(val, rule)
                if not ok:
                    expect_results.append(ExpectResult(is_pass=False, message="NotMatch", node=root_dot_key, val=val, expect=rule))
                else:
                    expect_results.append(ExpectResult(is_pass=True, message="OK", node=root_dot_key, val=val, expect=rule))
            else:
                val = vals[key]
                if val != rule:
                    expect_results.append(ExpectResult(is_pass=False, message="NotEqual", node=root_dot_key, val=val, expect=rule))
                else:
                    expect_results.append(ExpectResult(is_pass=True, message="OK", node=root_dot_key, val=val, expect=rule))


def expect_val(val, rule):
    res = eval(rule)
    if not isinstance(res, bool):
        raise Exception("rule should return result")
    return res


def to_time(val) -> datetime:
    return parser.parse(val)
