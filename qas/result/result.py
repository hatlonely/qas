#!/usr/bin/env python3


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
    req: dict
    res: dict
    expects: list[ExpectResult]
    is_pass: bool
    is_err: bool
    err: str
    succ: int
    fail: int

    def __init__(self, step=""):
        self.step = step
        self.expects = list[ExpectResult]()
        self.is_pass = True
        self.is_err = False
        self.err = ""
        self.succ = 0
        self.fail = 0
        self.req = {}
        self.res = {}

    def summary(self):
        if self.is_err:
            self.is_pass = False
            return
        self.succ = sum(1 for i in self.expects if i.is_pass)
        self.fail = len(self.expects) - self.succ
        self.is_pass = self.fail == 0

    def set_error(self, message):
        self.is_err = True
        self.fail = True
        self.err = message


@dataclass
class CaseResult:
    case: str
    before_steps: list[StepResult]
    steps: list[StepResult]
    after_steps: list[StepResult]
    is_pass: bool

    def __init__(self, case=""):
        self.case = case
        self.before_steps = list[StepResult]()
        self.steps = list[StepResult]()
        self.after_steps = list[StepResult]()
        self.is_pass = True

    def summary(self):
        for r in self.steps:
            r.summary()
        self.is_pass = all(i.is_pass for i in self.steps)


@dataclass
class TestResult:
    name: str
    setups: list[CaseResult]
    cases: list[CaseResult]
    teardowns: list[CaseResult]
    is_pass: bool
    succ: int
    fail: int
    skip: int
    sub_tests: list

    def __init__(self, name=""):
        self.name = name
        self.setups = list[CaseResult]()
        self.cases = list[CaseResult]()
        self.teardowns = list[CaseResult]()
        self.sub_tests = list[TestResult]()
        self.is_pass = True
        self.succ = 0
        self.fail = 0
        self.skip = 0
