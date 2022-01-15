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

