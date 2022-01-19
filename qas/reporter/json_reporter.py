#!/usr/bin/env python3


import json
from .reporter import Reporter
from ..result import TestResult, CaseResult, StepResult, ExpectResult


class JsonReporter(Reporter):
    def report_test_end(self, res: TestResult):
        print(json.dumps(JsonReporter.test_summary(res), indent=True))

    @staticmethod
    def test_summary(res: TestResult) -> dict:
        return {
            "isPass": res.is_pass,
            "succ": res.case_succ,
            "fail": res.case_fail,
            "skip": res.case_skip,
            "name": res.name,
            "cases": [JsonReporter.case_summary(i) for i in res.cases],
            "setups": [JsonReporter.case_summary(i) for i in res.setups],
            "teardowns": [JsonReporter.case_summary(i) for i in res.teardowns],
            "subTests": [JsonReporter.test_summary(i) for i in res.sub_tests],
        }

    @staticmethod
    def case_summary(res: CaseResult) -> dict:
        return {
            "isPass": res.is_pass,
            "case": res.case,
            "steps": [JsonReporter.step_summary(i) for i in res.steps]
        }

    @staticmethod
    def step_summary(res: StepResult) -> dict:
        return {
            "isPass": res.is_pass,
            "step": res.step,
            "succ": res.assertion_succ,
            "fail": res.assertion_fail,
            "req": res.req,
            "res": res.res,
            "expects": [JsonReporter.expect_summary(i) for i in res.expects],
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
