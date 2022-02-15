#!/usr/bin/env python3


import json
from types import SimpleNamespace

from ..util import merge


i18n = {
    "dft": {
        "title": {
            "report": "REPORT",
            "test": "TEST",
        },
        "status": {
            "pass": "PASS",
            "skip": "SKIP",
            "fail": "FAIL",
        },
        "summary": {
            "caseTotal": "TOTAL CASE",
            "casePass": "CASE PASS",
            "caseSkip": "CASE SKIP",
            "caseFail": "CASE FAIL",
            "stepPass": "STEP PASS",
            "stepSkip": "STEP SKIP",
            "stepFail": "STEP FAIL",
            "assertionPass": "ASSERTION PASS",
            "assertionFail": "ASSERTION FAIL",
            "elapse": "ELAPSE",
        },
        "testHeader": {
            "description": "Description",
            "err": "Err",
            "setUp": "SetUp",
            "case": "Case",
            "tearDown": "TearDown",
            "subTest": "SubTest",
        },
        "caseHeader": {
            "description": "Description",
            "command": "Command",
            "beforeCaseStep": "BeforeCaseStep",
            "preStep": "PreStep",
            "step": "Step",
            "postStep": "PostStep",
            "afterCaseStep": "AfterCaseStep",
        },
        "stepHeader": {
            "description": "Description",
            "req": "Req",
            "res": "Res",
            "err": "Err",
        },
        "toolTips": {
            "copy": "copy"
        }
    },
    "en": {},
    "zh": {
        "title": {
            "report": "测试报告",
            "test": "测试",
        },
        "status": {
            "pass": "通过",
            "skip": "跳过",
            "fail": "失败",
        },
        "testTitle": {
            "name": "测试报告",
            "pass": "测试通过",
            "skip": "测试跳过",
            "fail": "测试失败",
        },
        "summary": {
            "caseTotal": "测试总数",
            "casePass": "测试通过",
            "caseSkip": "测试跳过",
            "caseFail": "测试失败",
            "stepPass": "步骤通过",
            "stepSkip": "步骤跳过",
            "stepFail": "步骤失败",
            "assertionPass": "断言通过",
            "assertionFail": "断言失败",
            "elapse": "耗时",
        },
        "toolTips": {
            "copy": "复制"
        }
    }
}


class I18n:
    def __init__(self, args):
        args = merge(args, {
            "lang": "dft",
            "i18n": {},
        })

        self.i18n_ = json.loads(
            json.dumps(merge(args["i18n"], merge(i18n[args["lang"]], i18n["dft"]))),
            object_hook=lambda x: SimpleNamespace(**x),
        )

    def i18n(self):
        return self.i18n_
