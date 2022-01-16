#!/usr/bin/env python3

import yaml
import traceback
import os

from ..driver import HttpDriver, POPDriver, OTSDriver, ShellDriver, MysqlDriver, merge, REQUIRED
from ..assertion import expect_obj
from ..result import TestResult, CaseResult, StepResult, ExpectResult
from ..reporter import TextReporter, JsonReporter


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
    ctx = dict()
    req = dict()
    case_name = None

    def __init__(self, test_directory, case_directory=None, case_name=None):
        self.case_name = case_name
        if os.path.isfile(test_directory):
            fp = open(test_directory, "r", encoding="utf-8")
            data = yaml.safe_load(fp)
            fp.close()
            data = merge(data, {
                "name": REQUIRED,
                "case": []
            })
            self.data = data
            self.name = data["name"]
            for key in data["ctx"]:
                val = merge(data["ctx"][key], {
                    "type": REQUIRED,
                    "args": {},
                    "req": {},
                })
                self.ctx[key] = drivers[val["type"]](val["args"])
                self.req[key] = val["req"]
            self.case = data["case"]
        else:
            # load ctx.yaml
            ctx_filename = "{}/ctx.yaml".format(test_directory)
            if not os.path.exists(ctx_filename) or not os.path.isfile(ctx_filename):
                raise Exception("ctx.yaml is missing")
            fp = open("{}/ctx.yaml".format(test_directory), "r", encoding="utf-8")
            data = yaml.safe_load(fp)
            data = merge(data, {
                "name": REQUIRED,
                "case": []
            })
            self.data = data
            self.name = data["name"]
            for key in data["ctx"]:
                val = merge(data["ctx"][key], {
                    "type": REQUIRED,
                    "args": {},
                    "req": {},
                })
                self.ctx[key] = drivers[val["type"]](val["args"])
                self.req[key] = val["req"]
            self.case = data["case"]
            # load cases
            if not case_directory:
                for prefix, _, filenames in os.walk("{}/cases".format(test_directory)):
                    for filename in filenames:
                        for c in self.load_case_from_file("{}/{}".format(prefix, filename)):
                            self.case.append(c)
            else:
                for cd in case_directory.split(","):
                    for filename in os.listdir("{}/cases/{}".format(test_directory, cd)):
                        for c in self.load_case_from_file("{}/cases/{}/{}".format(test_directory, cd, filename)):
                            self.case.append(c)

    def load_case_from_file(self, filename):
        fp = open(filename, "r", encoding="utf-8")
        data = yaml.safe_load(fp)
        fp.close()
        if isinstance(data, dict):
            data["name"] = "{}/{}".format(filename, data["name"])
            yield data
        if isinstance(data, list):
            for item in data:
                item["name"] = "{}/{}".format(filename, item["name"])
                yield item

    def run(self):
        test_result = TestResult(self.name)
        for case in self.case:
            if self.case_name and self.case_name != case["name"]:
                continue
            case_result = CaseResult(case["name"])
            for idx, step in enumerate(case["step"]):
                if "name" not in step:
                    step["name"] = "step-{}".format(idx)
                step_result = StepResult(step["name"])
                try:
                    req = merge(step["req"], self.req[step["ctx"]])
                    step_result.req = req
                    res = self.ctx[step["ctx"]].do(req)
                    step_result.res = res
                    res = expect_obj(res, step["res"])
                    step_result.expect_results.extend(res)
                except Exception as e:
                    step_result.expect_results.append(ExpectResult(
                        is_pass=False, message="Exception {}".format(traceback.format_exc()), node="", val="", expect=""
                    ))
                case_result.step_results.append(step_result)
            test_result.case_results.append(case_result)
        print(reporters["text"].report(test_result))
        return test_result.is_pass
