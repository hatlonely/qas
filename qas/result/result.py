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

    def to_json(self):
        return {
            "isPass": self.is_pass,
            "message": self.message,
            "node": self.node,
            "val": self.val,
            "expect": self.expect,
        }

    @staticmethod
    def from_json(obj):
        res = ExpectResult(
            is_pass=obj["isPass"],
            message=obj["message"],
            node=obj["node"],
            val=obj["val"],
            expect=obj["expect"],
        )
        return res

@dataclass
class SubStepResult:
    is_pass: bool
    is_err: bool
    err: str
    req: dict
    res: dict
    assertions: list[ExpectResult]
    assertion_succ: int
    assertion_fail: int
    elapse: timedelta

    def to_json(self):
        return {
            "isPass": self.is_pass,
            "isErr": self.is_err,
            "err": self.err,
            "req": self.req,
            "res": self.res,
            "assertions":  self.assertions,
            "assertionSucc": self.assertion_succ,
            "assertionFail": self.assertion_fail,
            "elapse": int(self.elapse.microseconds),
        }

    @staticmethod
    def from_json(obj):
        res = SubStepResult()
        res.is_pass = obj["isPass"]
        res.is_err = obj["isErr"]
        res.err = obj["err"]
        res.req = obj["req"]
        res.res = obj["res"]
        res.assertions = [ExpectResult.from_json(i) for i in obj["assertions"]]
        res.assertion_succ = obj["assertionSucc"]
        res.assertion_fail = obj["assertionFail"]
        res.elapse = timedelta(microseconds=obj["elapse"])
        return res

    def __init__(self):
        self.is_pass = True
        self.is_err = False
        self.err = ""
        self.req = {}
        self.res = {}
        self.assertions = list[ExpectResult]()
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.elapse = timedelta(seconds=0)

    def set_error(self, message):
        self.is_pass = False
        self.is_err = True
        self.err = message
        self.assertion_fail += 1

    def add_expect_result(self, result):
        self.assertions = result
        self.assertion_succ += sum(1 for i in self.assertions if i.is_pass)
        self.assertion_fail += len(self.assertions) - self.assertion_succ
        self.is_pass = self.assertion_fail == 0


@dataclass
class StepResult:
    name: str
    description: str
    ctx: str
    is_skip: bool
    is_pass: bool
    req: dict
    res: dict
    sub_steps: list[SubStepResult]
    assertion_succ: int
    assertion_fail: int
    elapse: timedelta

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "ctx": self.ctx,
            "isSkip": self.is_skip,
            "isPass": self.is_pass,
            "req": self.req,
            "res": self.res,
            "subSteps": self.sub_steps,
            "assertionSucc": self.assertion_succ,
            "assertionFail": self.assertion_fail,
            "elapse": int(self.elapse.microseconds),
        }

    @staticmethod
    def from_json(obj):
        res = StepResult(obj["name"], obj["ctx"], description=obj["description"])
        res.is_skip = obj["isSkip"]
        res.is_pass = obj["isPass"]
        res.req = obj["req"]
        res.res = obj["res"]
        res.sub_steps = [SubStepResult.from_json(i) for i in obj["subSteps"]]
        res.assertion_succ = obj["assertionSucc"]
        res.assertion_fail = obj["assertionFail"]
        res.elapse = timedelta(microseconds=obj["elapse"])
        return res

    def __init__(self, name, ctx, description="", is_skip=False):
        self.name = name
        self.ctx = ctx
        self.description = description
        self.is_skip = is_skip
        self.is_pass = True
        self.req = {}
        self.res = {}
        self.sub_steps = list[SubStepResult]()
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.elapse = timedelta(seconds=0)

    def add_sub_step_result(self, result: SubStepResult):
        self.sub_steps.append(result)
        self.assertion_succ += result.assertion_succ
        self.assertion_fail += result.assertion_fail
        self.is_pass = self.assertion_fail == 0


@dataclass
class CaseResult:
    name: str
    description: str
    before_case_steps: list[StepResult]
    pre_steps: list[StepResult]
    steps: list[StepResult]
    post_steps: list[StepResult]
    after_case_steps: list[StepResult]
    is_pass: bool
    is_skip: bool
    step_succ: int
    step_fail: int
    step_skip: int
    assertion_succ: int
    assertion_fail: int
    elapse: timedelta

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "elapse": int(self.elapse.microseconds),
            "isPass": self.is_pass,
            "isSkip": self.is_skip,
            "steps": self.steps,
            "beforeCaseSteps": self.before_case_steps,
            "afterCaseSteps": self.after_case_steps,
            "stepSucc": self.step_succ,
            "stepFail": self.step_fail,
            "assertionSucc": self.assertion_succ,
            "assertionFail": self.assertion_fail,
        }

    @staticmethod
    def from_json(obj):
        res = CaseResult(name=obj["name"], description=obj["description"])
        res.is_skip = obj["isSkip"]
        res.is_pass = obj["isPass"]
        res.before_case_steps = [StepResult.from_json(i) for i in obj["beforeCaseSteps"]]
        res.steps = [StepResult.from_json(i) for i in obj["steps"]]
        res.after_case_steps = [StepResult.from_json(i) for i in obj["afterCaseSteps"]]
        res.step_succ = obj["stepSucc"]
        res.step_fail = obj["stepFail"]
        res.assertion_succ = obj["assertionSucc"]
        res.assertion_fail = obj["assertionFail"]
        res.elapse = timedelta(microseconds=obj["elapse"])
        return res

    def __init__(self, name, description="", is_skip=False):
        self.name = name
        self.description = description
        self.is_skip = is_skip
        self.before_case_steps = list[StepResult]()
        self.pre_steps = list[StepResult]()
        self.steps = list[StepResult]()
        self.post_steps = list[StepResult]()
        self.after_case_steps = list[StepResult]()
        self.is_pass = True
        self.elapse = timedelta(seconds=0)
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.step_succ = 0
        self.step_fail = 0
        self.step_skip = 0

    def add_case_step_result(self, step: StepResult):
        self.steps.append(step)
        if step.is_skip:
            self.step_skip += 1
        elif not step.is_pass:
            self.is_pass = False
            self.step_fail += 1
        else:
            self.step_succ += 1
        self.assertion_succ += step.assertion_succ
        self.assertion_fail += step.assertion_fail

    def add_case_pre_step_result(self, step: StepResult):
        self.pre_steps.append(step)
        if step.is_skip:
            self.step_skip += 1
        elif not step.is_pass:
            self.is_pass = False
            self.step_fail += 1
        else:
            self.step_succ += 1
        self.assertion_succ += step.assertion_succ
        self.assertion_fail += step.assertion_fail

    def add_case_post_step_result(self, step: StepResult):
        self.post_steps.append(step)
        if step.is_skip:
            self.step_skip += 1
        elif not step.is_pass:
            self.is_pass = False
            self.step_fail += 1
        else:
            self.step_succ += 1
        self.assertion_succ += step.assertion_succ
        self.assertion_fail += step.assertion_fail

    def add_before_case_step_result(self, step: StepResult):
        self.before_case_steps.append(step)
        if not step.is_pass:
            self.is_pass = False

    def add_after_case_step_result(self, step: StepResult):
        self.after_case_steps.append(step)
        if not step.is_pass:
            self.is_pass = False

@dataclass
class TestResult:
    directory: str
    name: str
    description: str
    is_skip: bool
    is_pass: bool
    is_err: bool
    err: str
    setups: list[CaseResult]
    cases: list[CaseResult]
    teardowns: list[CaseResult]
    sub_tests: list
    elapse: timedelta
    sub_tests: list
    case_succ: int
    case_fail: int
    case_skip: int
    step_succ: int
    step_fail: int
    step_skip: int
    assertion_succ: int
    assertion_fail: int
    curr_case_succ: int
    curr_case_fail: int
    curr_case_skip: int
    sub_test_succ: int
    sub_test_fail: int

    def to_json(self):
        return {
            "directory": self.directory,
            "name": self.name,
            "description": self.description,
            "isPass": self.is_pass,
            "isErr": self.is_err,
            "err": self.err,
            "elapse": int(self.elapse.microseconds),
            "caseSucc": self.case_succ,
            "caseFail": self.case_fail,
            "caseSkip": self.case_skip,
            "currCaseSucc": self.curr_case_succ,
            "currCaseFail": self.curr_case_fail,
            "currCaseSkip": self.curr_case_skip,
            "stepSucc": self.step_succ,
            "stepFail": self.step_fail,
            "stepSkip": self.step_skip,
            "assertionSucc": self.assertion_succ,
            "assertionFail": self.assertion_fail,
            "subTestSucc": self.sub_test_succ,
            "subTestFail": self.sub_test_fail,
            "cases": self.cases,
            "setups": self.setups,
            "teardowns": self.teardowns,
            "subTests": self.sub_tests,
        }

    @staticmethod
    def from_json(obj):
        res = TestResult(directory=obj["directory"], name=obj["name"], description=obj["description"])
        res.is_pass = obj["isPass"]
        res.is_err = obj["isErr"]
        res.err = obj["err"]
        res.setups = [CaseResult.from_json(i) for i in obj["setups"]]
        res.cases = [CaseResult.from_json(i) for i in obj["cases"]]
        res.teardowns = [CaseResult.from_json(i) for i in obj["teardowns"]]
        res.sub_tests = [TestResult.from_json(i) for i in obj["subTests"]]
        res.case_succ = obj["caseSucc"]
        res.case_fail = obj["caseFail"]
        res.case_skip = obj["caseSkip"]
        res.curr_case_succ = obj["currCaseSucc"]
        res.curr_case_fail = obj["currCaseFail"]
        res.curr_case_skip = obj["currCaseSkip"]
        res.step_succ = obj["stepSucc"]
        res.step_fail = obj["stepFail"]
        res.step_skip = obj["stepSkip"]
        res.assertion_succ = obj["assertionSucc"]
        res.assertion_fail = obj["assertionFail"]
        res.sub_test_succ = obj["subTestSucc"]
        res.sub_test_fail = obj["subTestFail"]
        res.elapse = timedelta(microseconds=obj["elapse"])
        return res

    def __init__(self, directory, name, description="", err_message=None, is_skip=False):
        self.directory = directory
        self.name = name
        self.description = description
        self.is_skip = is_skip
        self.is_pass = True
        self.is_err = False
        self.err = ""
        self.setups = list[CaseResult]()
        self.cases = list[CaseResult]()
        self.teardowns = list[CaseResult]()
        self.sub_tests = list[TestResult]()
        self.elapse = timedelta(seconds=0)
        self.case_succ = 0
        self.case_fail = 0
        self.case_skip = 0
        self.curr_case_succ = 0
        self.curr_case_fail = 0
        self.curr_case_skip = 0
        self.assertion_succ = 0
        self.assertion_fail = 0
        self.step_succ = 0
        self.step_fail = 0
        self.step_skip = 0
        self.sub_test_succ = 0
        self.sub_test_fail = 0
        if err_message:
            self.is_pass = False
            self.is_err = True
            self.err = err_message
            self.case_fail += 1

    def add_setup_result(self, case: CaseResult):
        self.setups.append(case)
        if not case.is_pass:
            self.is_pass = False
            self.case_fail += 1

    def add_case_result(self, case: CaseResult):
        self.cases.append(case)
        if case.is_skip:
            self.case_skip += 1
            self.curr_case_skip += 1
        elif not case.is_pass:
            self.case_fail += 1
            self.is_pass = False
            self.curr_case_fail += 1
        else:
            self.case_succ += 1
            self.curr_case_succ += 1
        self.step_succ += case.step_succ
        self.step_fail += case.step_fail
        self.step_skip += case.step_skip
        self.assertion_succ += case.assertion_succ
        self.assertion_fail += case.assertion_fail

    def add_teardown_result(self, case):
        self.teardowns.append(case)
        if not case.is_pass:
            self.is_pass = False
            self.case_fail += 1

    def add_sub_test_result(self, sub_test):
        if self.is_skip:
            return
        self.sub_tests.append(sub_test)
        self.case_succ += sub_test.case_succ
        self.case_fail += sub_test.case_fail
        self.case_skip += sub_test.case_skip
        self.step_succ += sub_test.step_succ
        self.step_fail += sub_test.step_fail
        self.step_skip += sub_test.step_skip
        self.assertion_succ += sub_test.assertion_succ
        self.assertion_fail += sub_test.assertion_fail
        if not sub_test.is_pass:
            self.is_pass = False
            self.sub_test_fail += 1
        else:
            self.sub_test_succ += 1
