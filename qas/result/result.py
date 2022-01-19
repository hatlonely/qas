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

    def add_expect_result(self, result):
        self.expects = result
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

    def add_case_step_result(self, step: StepResult):
        self.steps.append(step)
        if not step.is_pass:
            self.is_pass = False
            self.step_fail += 1
        else:
            self.step_succ += 1
        self.assertion_succ += step.assertion_succ
        self.assertion_fail += step.assertion_fail

    def add_before_case_step_result(self, step: StepResult):
        self.before_steps.append(step)
        if not step.is_pass:
            self.is_pass = False
            self.step_fail += 1
        else:
            self.step_succ += 1
        self.assertion_succ += step.assertion_succ
        self.assertion_fail += step.assertion_fail

    def add_after_case_step_result(self, step: StepResult):
        self.after_steps.append(step)
        if not step.is_pass:
            self.is_pass = False
            self.step_fail += 1
        else:
            self.step_succ += 1
        self.assertion_succ += step.assertion_succ
        self.assertion_fail += step.assertion_fail


@dataclass
class TestResult:
    name: str
    setups: list[CaseResult]
    cases: list[CaseResult]
    teardowns: list[CaseResult]
    sub_tests: list
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

    def add_setup_result(self, case: CaseResult):
        self.setups.append(case)
        if not case.is_pass:
            self.is_pass = False

    def add_case_result(self, case):
        self.cases.append(case)
        if case.is_pass:
            self.case_succ += 1
        else:
            self.case_fail += 1
        self.step_succ += case.step_succ
        self.step_fail += case.step_fail
        self.assertion_succ += case.assertion_succ
        self.assertion_fail += case.assertion_fail

    def add_teardown_result(self, case):
        self.teardowns.append(case)
        if not case.is_pass:
            self.is_pass = False

    def add_sub_test_result(self, sub_test):
        self.sub_tests.append(sub_test)
        self.case_succ += sub_test.case_succ
        self.case_fail += sub_test.case_fail
        self.case_skip += sub_test.case_skip
        self.step_succ += sub_test.step_succ
        self.step_fail += sub_test.step_fail
        self.assertion_succ += sub_test.assertion_succ
        self.assertion_fail += sub_test.assertion_fail
        if not sub_test.is_pass:
            self.is_pass = False
