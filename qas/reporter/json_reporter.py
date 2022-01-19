#!/usr/bin/env python3


import json
import durationpy

from .reporter import Reporter
from ..result import TestResult, CaseResult, StepResult, ExpectResult


class JsonReporter(Reporter):
    def report_test_end(self, res: TestResult):
        print(json.dumps(JsonReporter.test_summary(res), indent=True))

    @staticmethod
    def test_summary(res: TestResult) -> dict:
        return {
            "name": res.name,
            "isPass": res.is_pass,
            "elapse": durationpy.to_str(res.elapse),
            "case_succ": res.case_succ,
            "case_fail": res.case_fail,
            "case_skip": res.case_skip,
            "step_succ": res.step_succ,
            "step_fail": res.step_fail,
            "assertion_succ": res.assertion_succ,
            "assertion_fail": res.assertion_fail,
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
            "step_succ": res.step_succ,
            "step_fail": res.step_fail,
            "assertion_succ": res.assertion_succ,
            "assertion_fail": res.assertion_fail,
        }

    @staticmethod
    def step_summary(res: StepResult) -> dict:
        return {
            "name": res.name,
            "isPass": res.is_pass,
            "isSkip": res.is_skip,
            "elapse": durationpy.to_str(res.elapse),
            "assertion_succ": res.assertion_succ,
            "assertion_fail": res.assertion_fail,
            "req": res.req,
            "res": res.res,
            "assertions": [JsonReporter.expect_summary(i) for i in res.assertions],
            "isErr": res.is_err,
            "err": res.err,
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
