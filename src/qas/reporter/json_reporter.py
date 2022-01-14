#!/usr/bin/env python3
import json

from src.qas.assertion.expect import TestResult, CaseResult, StepResult, ExpectResult


def report(res: TestResult) -> str:
    res.summary()
    return json.dumps(test_summary(res))


def test_summary(res: TestResult) -> dict:
    return {
        "isPass": res.is_pass,
        "succ": res.succ,
        "fail": res.fail,
        "name": res.name,
        "caseResults": [case_summary(i) for i in res.case_results]
    }


def case_summary(res: CaseResult) -> dict:
    return {
        "isPass": res.is_pass,
        "case": res.case,
        "stepResults": [step_summary(i) for i in res.step_results]
    }


def step_summary(res: StepResult) -> dict:
    return {
        "isPass": res.is_pass,
        "step": res.step,
        "succ": res.succ,
        "fail": res.fail,
        "expectResults": [expect_summary(i) for i in res.expect_results]
    }


def expect_summary(res: ExpectResult) -> dict:
    return {
        "isPass": res.is_pass,
        "message": res.message,
        "node": res.node,
        "val": res.val,
        "expect": res.expect,
    }