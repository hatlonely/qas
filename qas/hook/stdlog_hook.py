#!/usr/bin/env python3


import json
from datetime import datetime

from .hook import Hook
from ..result import TestResult, CaseResult, StepResult


class StdLogHook(Hook):
    def __init__(self, args):
        super().__init__(args)

    def on_exit(self, res: TestResult):
        StdLogHook.log(res.name, "test", res.status, res.elapse, {
            "casePass": res.case_pass,
            "caseFail": res.case_fail,
            "caseSkip": res.case_skip,
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_test_end(self, res: TestResult):
        StdLogHook.log(res.name, "subTest", res.status, res.elapse, {
            "casePass": res.case_pass,
            "caseFail": res.case_fail,
            "caseSkip": res.case_skip,
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_set_up_end(self, res: CaseResult):
        StdLogHook.log(res.name, "setUp", res.status, res.elapse, {
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_case_end(self, res: CaseResult):
        StdLogHook.log(res.name, "case", res.status, res.elapse, {
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_tear_down_end(self, res: CaseResult):
        StdLogHook.log(res.name, "tearDown", res.status, res.elapse, {
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_step_end(self, res: StepResult):
        if res.is_skip:
            status = "skip"
        elif res.is_pass:
            status = "pass"
        else:
            status = "fail"
        StdLogHook.log(res.name, "step", status, res.elapse, {
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    @staticmethod
    def log(name, type_, status, elapse, detail):
        print(json.dumps({
            "time": datetime.utcnow().replace(microsecond=0).isoformat(),
            "type": type_,
            "status": status,
            "elapseMs": int(elapse.total_seconds() * 1000),
            "detail": detail
        }))
