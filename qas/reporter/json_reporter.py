#!/usr/bin/env python3


import json
import durationpy

from ..result import TestResult, CaseResult, StepResult, SubStepResult, ExpectResult
from .reporter import Reporter


class JsonReporter(Reporter):
    def report_final_result(self, res: TestResult):
        print(json.dumps(JsonReporter.test_summary(res), indent=2, default=lambda x: x.__name__))

    @staticmethod
    def test_summary(res: TestResult) -> dict:
        return {
            "name": res.name,
            "isPass": res.is_pass,
            "elapse": durationpy.to_str(res.elapse),
            "caseSucc": res.case_succ,
            "caseFail": res.case_fail,
            "caseSkip": res.case_skip,
            "stepSucc": res.step_succ,
            "stepFail": res.step_fail,
            "assertionSucc": res.assertion_succ,
            "assertionFail": res.assertion_fail,
            "cases": [JsonReporter.case_summary(i) for i in res.cases],
            "setups": [JsonReporter.case_summary(i) for i in res.setups],
            "teardowns": [JsonReporter.case_summary(i) for i in res.teardowns],
            "subTests": [JsonReporter.test_summary(i) for i in res.sub_tests],
        }

    @staticmethod
    def case_summary(res: CaseResult) -> dict:
        return {
            "name": res.name,
            "elapse": durationpy.to_str(res.elapse),
            "isPass": res.is_pass,
            "isSkip": res.is_skip,
            "steps": [JsonReporter.step_summary(i) for i in res.steps],
            "beforeCaseSteps": [JsonReporter.step_summary(i) for i in res.before_case_steps],
            "afterCaseSteps": [JsonReporter.step_summary(i) for i in res.after_case_steps],
            "stepSucc": res.step_succ,
            "stepFail": res.step_fail,
            "assertionSucc": res.assertion_succ,
            "assertionFail": res.assertion_fail,
        }

    @staticmethod
    def step_summary(res: StepResult) -> dict:
        return {
            "name": res.name,
            "isSkip": res.is_skip,
            "isPass": res.is_pass,
            "req": res.req,
            "res": res.res,
            "subSteps": [JsonReporter.sub_step_summary(i) for i in res.sub_steps],
            "assertionSucc": res.assertion_succ,
            "assertionFail": res.assertion_fail,
            "elapse": durationpy.to_str(res.elapse),
        }

    @staticmethod
    def sub_step_summary(res: SubStepResult) -> dict:
        return {
            "isPass": res.is_pass,
            "isErr": res.is_err,
            "err": res.err,
            "req": res.req,
            "res": res.res,
            "assertions":  [JsonReporter.expect_summary(i) for i in res.assertions],
            "assertionSucc": res.assertion_succ,
            "assertionFail": res.assertion_fail,
            "elapse": durationpy.to_str(res.elapse),
        }

    @staticmethod
    def expect_summary(res: ExpectResult) -> dict:
        return {
            "isPass": res.is_pass,
            "message": res.message,
            "node": res.node,
            "val": res.val,
            "expect": res.expect,
        }
