#!/usr/bin/env python3
import re

import yaml
import traceback
import os
import json
from types import SimpleNamespace

from ..driver import HttpDriver, POPDriver, OTSDriver, ShellDriver, MysqlDriver, merge, REQUIRED
from ..assertion import expect, render
from ..result import TestResult, CaseResult, StepResult
from ..reporter import TextReporter, JsonReporter


def dict_to_sns(d):
    return SimpleNamespace(**d)


drivers = {
    "http": HttpDriver,
    "pop": POPDriver,
    "ots": OTSDriver,
    "shell": ShellDriver,
    "mysql": MysqlDriver,
}

reporters = {
    "text": TextReporter,
    "json": JsonReporter,
}


class Framework:
    data = None
    case = None
    name = None
    set_up = None
    tear_down = None
    ctx = dict()
    var = dict()
    req = dict()
    case_name = None
    case_regex = None
    skip_setup = False
    skip_teardown = False

    def __init__(self, test_directory, case_directory=None, case_name=None, case_regex=None, skip_setup=False, skip_teardown=False):
        self.case_name = case_name
        self.case_regex = case_regex
        self.skip_setup = skip_setup
        self.skip_teardown = skip_teardown
        if os.path.isfile(test_directory):
            self.load_ctx(test_directory)
            return

        # load ctx.yaml
        self.load_ctx("{}/ctx.yaml".format(test_directory))
        # load cases
        if not case_directory:
            for prefix, _, filenames in os.walk("{}/cases".format(test_directory)):
                for filename in filenames:
                    for c in self.load_case("{}/{}".format(prefix, filename)):
                        self.case.append(c)
        else:
            for cd in case_directory.split(","):
                for filename in os.listdir("{}/cases/{}".format(test_directory, cd)):
                    for c in self.load_case("{}/cases/{}/{}".format(test_directory, cd, filename)):
                        self.case.append(c)

        if os.path.isfile("{}/setup.yaml".format(test_directory)):
            for c in self.load_case("{}/setup.yaml".format(test_directory)):
                self.set_up.append(c)

        if os.path.isfile("{}/teardown.yaml".format(test_directory)):
            for c in self.load_case("{}/teardown.yaml".format(test_directory)):
                self.tear_down.append(c)

    def load_ctx(self, ctx_filename):
        if not os.path.exists(ctx_filename) or not os.path.isfile(ctx_filename):
            raise Exception("ctx file [{}] is missing".format(ctx_filename))
        fp = open(ctx_filename, "r", encoding="utf-8")
        data = yaml.safe_load(fp)
        fp.close()
        data = merge(data, {
            "name": REQUIRED,
            "ctx": REQUIRED,
            "var": {},
            "case": [],
            "setUp": [],
            "tearDown": [],
        })
        self.data = data
        self.var = json.loads(json.dumps(data["var"]), object_hook=dict_to_sns)
        self.name = data["name"]
        for key in data["ctx"]:
            val = merge(data["ctx"][key], {
                "type": REQUIRED,
                "args": {},
                "req": {},
            })
            val = render(val, var=self.var)
            self.ctx[key] = drivers[val["type"]](val["args"])
            self.req[key] = val["req"]
        self.case = data["case"]
        self.set_up = data["setUp"]
        self.tear_down = data["tearDown"]

    def load_case(self, filename):
        fp = open(filename, "r", encoding="utf-8")
        data = yaml.safe_load(fp)
        fp.close()
        if isinstance(data, dict):
            data = merge(data, {
                "name": REQUIRED,
            })
            data["name"] = "{}/{}".format(filename, data["name"])
            yield data
        if isinstance(data, list):
            for item in data:
                item = merge(item, {
                    "name": REQUIRED,
                })
                item["name"] = "{}/{}".format(filename, item["name"])
                yield item

    def run(self):
        test_result = TestResult(self.name)
        if not self.skip_setup:
            for case in self.set_up:
                test_result.setups.append(self.run_case(case))
        for case in self.case:
            if self.case_name and self.case_name != case["name"]:
                test_result.skip += 1
                continue
            if self.case_regex and not re.search(self.case_regex, case["name"]):
                test_result.skip += 1
                continue
            test_result.cases.append(self.run_case(case))
        if not self.skip_teardown:
            for case in self.tear_down:
                test_result.teardowns.append(self.run_case(case))
        print(reporters["text"].report(test_result))
        return test_result.is_pass

    def run_case(self, case):
        case_result = CaseResult(case["name"])
        for idx, step in enumerate(case["step"]):
            step = merge(step, {
                "name": "step-{}".format(idx),
                "res": {},
            })
            step_result = StepResult(step["name"])
            try:
                req = merge(step["req"], self.req[step["ctx"]])
                req = render(req, case=case_result, var=self.var)
                step_result.req = req
                res = self.ctx[step["ctx"]].do(req)
                step_result.res = res
                result = expect(res, step["res"], case=case_result, var=self.var)
                step_result.expects.extend(result)
            except Exception as e:
                step_result.is_err = True
                step_result.err = "Exception {}".format(traceback.format_exc())
                step_result.is_pass = False
            case_result.steps.append(step_result)
            step_result.summary()
            if not step_result.is_pass:
                break
        return case_result
