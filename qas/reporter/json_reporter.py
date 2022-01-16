#!/usr/bin/env python3


import json
from ..result import TestResult, CaseResult, StepResult, ExpectResult


class JsonReporter:
    @staticmethod
    def report(res: TestResult) -> str:
        res.summary()
        return json.dumps(JsonReporter.test_summary(res))

    @staticmethod
    def test_summary(res: TestResult) -> dict:
        return {
            "isPass": res.is_pass,
            "succ": res.succ,
            "fail": res.fail,
            "name": res.name,
            "caseResults": [JsonReporter.case_summary(i) for i in res.cases]
        }

    @staticmethod
    def case_summary(res: CaseResult) -> dict:
        return {
            "isPass": res.is_pass,
            "case": res.case,
            "stepResults": [JsonReporter.step_summary(i) for i in res.steps]
        }

    @staticmethod
    def step_summary(res: StepResult) -> dict:
        return {
            "isPass": res.is_pass,
            "step": res.step,
            "succ": res.succ,
            "fail": res.fail,
            "req": res.req,
            "res": res.res,
            "expectResults": [JsonReporter.expect_summary(i) for i in res.expects]
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
