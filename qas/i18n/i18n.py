#!/usr/bin/env python3


import json
import locale
from types import SimpleNamespace

from ..util import merge


i18n = {
    "dft": {
        "title": {
            "report": "REPORT",
            "test": "TEST",
        },
        "status": {
            "succ": "PASS",
            "skip": "SKIP",
            "fail": "FAIL",
        },
        "summary": {
            "caseTotal": "Total Case",
            "casePass": "Case Pass",
            "caseSkip": "Case Skip",
            "caseFail": "Case Fail",
            "stepPass": "Step Pass",
            "stepSkip": "Step Skip",
            "stepFail": "Step Fail",
            "assertionPass": "Assertion Pass",
            "assertionFail": "Assertion Fail",
            "elapse": "Elapse",
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
            "subStep": "SubStep",
        },
        "toolTips": {
            "copy": "copy"
        }
    },
    "zh": {
        "title": {
            "report": "测试报告",
            "test": "测试",
        },
        "status": {
            "succ": "通过",
            "skip": "跳过",
            "fail": "失败",
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
        "testHeader": {
            "description": "描述",
            "err": "错误",
            "setUp": "测试环境准备",
            "case": "测试单元",
            "tearDown": "测试环境清理",
            "subTest": "子测试",
        },
        "caseHeader": {
            "description": "描述",
            "command": "命令",
            "beforeCaseStep": "测试开始前",
            "preStep": "前置步骤",
            "step": "步骤",
            "postStep": "后置步骤",
            "afterCaseStep": "测试结束后",
        },
        "stepHeader": {
            "description": "描述",
            "req": "请求",
            "res": "返回",
            "err": "错误",
            "subStep": "子步骤",
        },
        "toolTips": {
            "copy": "复制"
        }
    }
}


class I18n:
    def __init__(self, args=None):
        lang = "dft"
        try:
            lang = locale.getdefaultlocale()[0].split('_')[0]
        except Exception as e:
            pass

        if args is None:
            args = {}
        args = merge(args, {
            "lang": lang,
            "i18n": {},
        })

        lang = args["lang"]
        if lang not in i18n:
            lang = "dft"

        self.i18n_ = json.loads(
            json.dumps(merge(args["i18n"], merge(i18n[lang], i18n["dft"]))),
            object_hook=lambda x: SimpleNamespace(**x),
        )

    def i18n(self):
        return self.i18n_
