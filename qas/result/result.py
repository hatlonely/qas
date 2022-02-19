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
    assertion_pass: int
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
            "assertionPass": self.assertion_pass,
            "assertionFail": self.assertion_fail,
            "elapse": int(self.elapse.total_seconds() * 1000000),
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
        res.assertion_pass = obj["assertionPass"]
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
        self.assertion_pass = 0
        self.assertion_fail = 0
        self.elapse = timedelta(seconds=0)

    def set_error(self, message):
        self.is_pass = False
        self.is_err = True
        self.err = message
        self.assertion_fail += 1

    def add_expect_result(self, result):
        self.assertions = result
        self.assertion_pass += sum(1 for i in self.assertions if i.is_pass)
        self.assertion_fail += len(self.assertions) - self.assertion_pass
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
    assertion_pass: int
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
            "assertionPass": self.assertion_pass,
            "assertionFail": self.assertion_fail,
            "elapse": int(self.elapse.total_seconds() * 1000000),
        }

    @staticmethod
    def from_json(obj):
        res = StepResult(obj["name"], obj["ctx"], description=obj["description"])
        res.is_skip = obj["isSkip"]
        res.is_pass = obj["isPass"]
        res.req = obj["req"]
        res.res = obj["res"]
        res.sub_steps = [SubStepResult.from_json(i) for i in obj["subSteps"]]
        res.assertion_pass = obj["assertionPass"]
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
        self.assertion_pass = 0
        self.assertion_fail = 0
        self.elapse = timedelta(seconds=0)

    def add_sub_step_result(self, result: SubStepResult):
        self.req = result.req
        self.res = result.res
        self.sub_steps.append(result)
        self.assertion_pass += result.assertion_pass
        self.assertion_fail += result.assertion_fail
        self.is_pass = self.assertion_fail == 0


@dataclass
class CaseResult:
    id_: str
    name: str
    directory: str
    description: str
    command: str
    status: str
    before_case_steps: list[StepResult]
    pre_steps: list[StepResult]
    steps: list[StepResult]
    post_steps: list[StepResult]
    after_case_steps: list[StepResult]
    is_pass: bool
    is_skip: bool
    step_pass: int
    step_fail: int
    step_skip: int
    assertion_pass: int
    assertion_fail: int
    elapse: timedelta

    def to_json(self):
        return {
            "id": self.id_,
            "name": self.name,
            "directory": self.directory,
            "description": self.description,
            "command": self.command,
            "status": self.status,
            "elapse": int(self.elapse.total_seconds() * 1000000),
            "isPass": self.is_pass,
            "isSkip": self.is_skip,
            "steps": self.steps,
            "beforeCaseSteps": self.before_case_steps,
            "afterCaseSteps": self.after_case_steps,
            "stepPass": self.step_pass,
            "stepFail": self.step_fail,
            "assertionPass": self.assertion_pass,
            "assertionFail": self.assertion_fail,
        }

    @staticmethod
    def from_json(obj):
        res = CaseResult(directory=obj["directory"], id_=obj["id"], name=obj["name"], description=obj["description"])
        res.command = obj["command"]
        res.status = obj["status"]
        res.is_skip = obj["isSkip"]
        res.is_pass = obj["isPass"]
        res.before_case_steps = [StepResult.from_json(i) for i in obj["beforeCaseSteps"]]
        res.steps = [StepResult.from_json(i) for i in obj["steps"]]
        res.after_case_steps = [StepResult.from_json(i) for i in obj["afterCaseSteps"]]
        res.step_pass = obj["stepPass"]
        res.step_fail = obj["stepFail"]
        res.assertion_pass = obj["assertionPass"]
        res.assertion_fail = obj["assertionFail"]
        res.elapse = timedelta(microseconds=obj["elapse"])
        return res

    def __init__(self, directory, id_, name, description="", command="", is_skip=False):
        self.id_ = id_
        self.name = name
        self.directory = directory
        self.description = description
        self.command = command
        self.status = "pass"
        self.is_skip = is_skip
        self.before_case_steps = list[StepResult]()
        self.pre_steps = list[StepResult]()
        self.steps = list[StepResult]()
        self.post_steps = list[StepResult]()
        self.after_case_steps = list[StepResult]()
        self.is_pass = True
        self.elapse = timedelta(seconds=0)
        self.assertion_pass = 0
        self.assertion_fail = 0
        self.step_pass = 0
        self.step_fail = 0
        self.step_skip = 0
        if is_skip:
            self.status = "skip"

    def add_case_step_result(self, step: StepResult):
        self.steps.append(step)
        if step.is_skip:
            self.step_skip += 1
        elif not step.is_pass:
            self.is_pass = False
            self.status = "fail"
            self.step_fail += 1
        else:
            self.step_pass += 1
        self.assertion_pass += step.assertion_pass
        self.assertion_fail += step.assertion_fail

    def add_case_pre_step_result(self, step: StepResult):
        self.pre_steps.append(step)
        if step.is_skip:
            self.step_skip += 1
        elif not step.is_pass:
            self.is_pass = False
            self.status = "fail"
            self.step_fail += 1
        else:
            self.step_pass += 1
        self.assertion_pass += step.assertion_pass
        self.assertion_fail += step.assertion_fail

    def add_case_post_step_result(self, step: StepResult):
        self.post_steps.append(step)
        if step.is_skip:
            self.step_skip += 1
        elif not step.is_pass:
            self.is_pass = False
            self.status = "fail"
            self.step_fail += 1
        else:
            self.step_pass += 1
        self.assertion_pass += step.assertion_pass
        self.assertion_fail += step.assertion_fail

    def add_before_case_step_result(self, step: StepResult):
        self.before_case_steps.append(step)
        if not step.is_pass:
            self.is_pass = False
            self.status = "fail"

    def add_after_case_step_result(self, step: StepResult):
        self.after_case_steps.append(step)
        if not step.is_pass:
            self.is_pass = False
            self.status = "fail"

@dataclass
class TestResult:
    directory: str
    name: str
    description: str
    status: str
    is_skip: bool
    is_pass: bool
    is_err: bool
    err: str
    set_ups: list[CaseResult]
    cases: list[CaseResult]
    tear_downs: list[CaseResult]
    sub_tests: list
    elapse: timedelta
    sub_tests: list
    case_pass: int
    case_fail: int
    case_skip: int
    set_up_pass: int
    set_up_fail: int
    tear_down_pass: int
    tear_down_fail: int
    step_pass: int
    step_fail: int
    step_skip: int
    assertion_pass: int
    assertion_fail: int
    curr_case_pass: int
    curr_case_fail: int
    curr_case_skip: int
    sub_test_pass: int
    sub_test_skip: int
    sub_test_fail: int

    def to_json(self):
        return {
            "directory": self.directory,
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "isSkip": self.is_skip,
            "isPass": self.is_pass,
            "isErr": self.is_err,
            "err": self.err,
            "elapse": int(self.elapse.total_seconds() * 1000000),
            "casePass": self.case_pass,
            "caseFail": self.case_fail,
            "caseSkip": self.case_skip,
            "setUpPass": self.set_up_pass,
            "setUpFail": self.set_up_fail,
            "tearDownPass": self.tear_down_pass,
            "tearDownFail": self.tear_down_fail,
            "currCasePass": self.curr_case_pass,
            "currCaseFail": self.curr_case_fail,
            "currCaseSkip": self.curr_case_skip,
            "stepPass": self.step_pass,
            "stepFail": self.step_fail,
            "stepSkip": self.step_skip,
            "assertionPass": self.assertion_pass,
            "assertionFail": self.assertion_fail,
            "subTestPass": self.sub_test_pass,
            "subTestSkip": self.sub_test_skip,
            "subTestFail": self.sub_test_fail,
            "cases": self.cases,
            "setUps": self.set_ups,
            "tearDowns": self.tear_downs,
            "subTests": self.sub_tests,
        }

    @staticmethod
    def from_json(obj):
        res = TestResult(directory=obj["directory"], name=obj["name"], description=obj["description"], err_message=obj["err"], is_skip=obj["isSkip"])
        res.is_pass = obj["isPass"]
        res.status = obj["status"]
        res.set_ups = [CaseResult.from_json(i) for i in obj["setUps"]]
        res.cases = [CaseResult.from_json(i) for i in obj["cases"]]
        res.tear_downs = [CaseResult.from_json(i) for i in obj["tearDowns"]]
        res.sub_tests = [TestResult.from_json(i) for i in obj["subTests"]]
        res.case_pass = obj["casePass"]
        res.case_fail = obj["caseFail"]
        res.case_skip = obj["caseSkip"]
        res.set_up_pass = obj["setUpPass"]
        res.set_up_fail = obj["setUpFail"]
        res.tear_down_pass = obj["tearDownPass"]
        res.tear_down_fail = obj["tearDownFail"]
        res.curr_case_pass = obj["currCasePass"]
        res.curr_case_fail = obj["currCaseFail"]
        res.curr_case_skip = obj["currCaseSkip"]
        res.step_pass = obj["stepPass"]
        res.step_fail = obj["stepFail"]
        res.step_skip = obj["stepSkip"]
        res.assertion_pass = obj["assertionPass"]
        res.assertion_fail = obj["assertionFail"]
        res.sub_test_pass = obj["subTestPass"]
        res.sub_test_skip = obj["subTestSkip"]
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
        self.set_ups = list[CaseResult]()
        self.cases = list[CaseResult]()
        self.tear_downs = list[CaseResult]()
        self.sub_tests = list[TestResult]()
        self.elapse = timedelta(seconds=0)
        self.case_pass = 0
        self.case_fail = 0
        self.case_skip = 0
        self.set_up_pass = 0
        self.set_up_fail = 0
        self.tear_down_pass = 0
        self.tear_down_fail = 0
        self.curr_case_pass = 0
        self.curr_case_fail = 0
        self.curr_case_skip = 0
        self.assertion_pass = 0
        self.assertion_fail = 0
        self.step_pass = 0
        self.step_fail = 0
        self.step_skip = 0
        self.sub_test_pass = 0
        self.sub_test_skip = 0
        self.sub_test_fail = 0
        if err_message:
            self.is_pass = False
            self.is_err = True
            self.err = err_message
            self.case_fail += 1
        if self.is_skip:
            self.status = "skip"
        elif self.is_pass:
            self.status = "pass"
        else:
            self.status = "fail"

    def add_set_up_result(self, case: CaseResult):
        self.set_ups.append(case)
        if not case.is_pass:
            self.is_pass = False
            self.status = "fail"
            self.set_up_fail += 1
        else:
            self.set_up_pass += 1

    def add_case_result(self, case: CaseResult):
        self.cases.append(case)
        if case.is_skip:
            self.case_skip += 1
            self.curr_case_skip += 1
        elif not case.is_pass:
            self.case_fail += 1
            self.is_pass = False
            self.status = "fail"
            self.curr_case_fail += 1
        else:
            self.case_pass += 1
            self.curr_case_pass += 1
        self.step_pass += case.step_pass
        self.step_fail += case.step_fail
        self.step_skip += case.step_skip
        self.assertion_pass += case.assertion_pass
        self.assertion_fail += case.assertion_fail

    def add_tear_down_result(self, case):
        self.tear_downs.append(case)
        if not case.is_pass:
            self.is_pass = False
            self.status = "fail"
            self.tear_down_fail += 1
        else:
            self.tear_down_pass += 1

    def add_sub_test_result(self, sub_test):
        if sub_test.case_pass + sub_test.case_skip + sub_test.case_fail == 0:
            return

        self.sub_tests.append(sub_test)
        if sub_test.is_skip:
            self.sub_test_skip += 1
            return
        self.case_pass += sub_test.case_pass
        self.case_fail += sub_test.case_fail
        self.case_skip += sub_test.case_skip
        self.step_pass += sub_test.step_pass
        self.step_fail += sub_test.step_fail
        self.step_skip += sub_test.step_skip
        self.assertion_pass += sub_test.assertion_pass
        self.assertion_fail += sub_test.assertion_fail
        if not sub_test.is_pass:
            self.is_pass = False
            self.status = "fail"
            self.sub_test_fail += 1
        else:
            self.sub_test_pass += 1
