#!/usr/bin/env python3


from dataclasses import dataclass
from datetime import timedelta


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
    req: dict
    res: dict
    expects: list[ExpectResult]
    is_pass: bool
    is_err: bool
    err: str
    assertion_succ: int
    assertion_fail: int
    elapse: timedelta

    def __init__(self, step=""):
        self.step = step
        self.expects = list[ExpectResult]()
        self.is_pass = True
        self.is_err = False
        self.err = ""
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.req = {}
        self.res = {}
        self.elapse = 0

    def summary(self):
        if self.is_err:
            self.is_pass = False
            return
        self.assertion_succ = sum(1 for i in self.expects if i.is_pass)
        self.assertion_fail = len(self.expects) - self.assertion_succ
        self.is_pass = self.assertion_fail == 0

    def set_error(self, message):
        self.is_err = True
        self.assertion_fail = True
        self.err = message


@dataclass
class CaseResult:
    case: str
    before_steps: list[StepResult]
    steps: list[StepResult]
    after_steps: list[StepResult]
    is_pass: bool
    step_succ: int
    step_fail: int
    assertion_succ: int
    assertion_fail: int
    elapse: timedelta

    def __init__(self, case=""):
        self.case = case
        self.before_steps = list[StepResult]()
        self.steps = list[StepResult]()
        self.after_steps = list[StepResult]()
        self.is_pass = True
        self.elapse = 0
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.step_succ = 0
        self.step_fail = 0


@dataclass
class TestResult:
    name: str
    setups: list[CaseResult]
    cases: list[CaseResult]
    teardowns: list[CaseResult]
    is_pass: bool
    case_succ: int
    case_fail: int
    case_skip: int
    sub_tests: list
    elapse: timedelta

    def __init__(self, name=""):
        self.name = name
        self.setups = list[CaseResult]()
        self.cases = list[CaseResult]()
        self.teardowns = list[CaseResult]()
        self.sub_tests = list[TestResult]()
        self.is_pass = True
        self.elapse = 0
        self.case_succ = 0
        self.case_fail = 0
        self.case_skip = 0
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.step_succ = 0
        self.step_fail = 0
