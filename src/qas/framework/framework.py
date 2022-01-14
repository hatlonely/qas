#!/usr/bin/env python3

import yaml
import traceback
import os

from src.qas.driver.http_driver import HttpDriver
from src.qas.driver.pop_driver import POPDriver
from src.qas.driver.ots_driver import OTSDriver
from src.qas.assertion.expect import expect_obj
from src.qas.assertion.expect import TestResult, CaseResult, StepResult, ExpectResult
from src.qas.reporter.text_reporter import TextReporter


drivers = {
    "http": HttpDriver,
    "pop": POPDriver,
    "ots": OTSDriver,
}

reporters = {
    "text": TextReporter,
}


class Framework:
    data = None
    case = None
    name = None
    ctx = dict()

    def __init__(self, case_directory):
        if os.path.isfile(case_directory):
            fp = open(case_directory, "r", encoding="utf-8")
            data = yaml.safe_load(fp)
            fp.close()
            self.data = data
            self.name = data["name"]
            for key in data["ctx"]:
                val = data["ctx"][key]
                self.ctx[key] = drivers[val["type"]](val["args"])
            self.case = data["case"]
        else:
            # load ctx.yaml
            ctx_filename = "{}/ctx.yaml".format(case_directory)
            if not os.path.exists(ctx_filename) or not os.path.isfile(ctx_filename):
                raise Exception("ctx.yaml is missing")
            fp = open("{}/ctx.yaml".format(case_directory), "r", encoding="utf-8")
            data = yaml.safe_load(fp)
            self.data = data
            self.name = data["name"]
            for key in data["ctx"]:
                val = data["ctx"][key]
                self.ctx[key] = drivers[val["type"]](val["args"])
            if "case" in data:
                self.case = data["case"]
            else:
                self.case = []
            # load cases
            for prefix, _, filenames in os.walk("{}/cases".format(case_directory)):
                for filename in filenames:
                    fp = open("{}/{}".format(prefix, filename), "r", encoding="utf-8")
                    data = yaml.safe_load(fp)
                    fp.close()
                    data["name"] = "{}/{}/{}".format(prefix, filename, data["name"])
                    self.case.append(data)

    def run(self):
        test_result = TestResult(self.name)
        for case in self.case:
            case_result = CaseResult(case["name"])
            for idx, step in enumerate(case["step"]):
                if "name" not in step:
                    step["name"] = "step-{}".format(idx)
                step_result = StepResult(step["name"])
                res = self.ctx[step["ctx"]].do(step["req"])
                try:
                    res = expect_obj(res, step["res"])
                    step_result.expect_results.extend(res)
                except Exception as e:
                    step_result.expect_results.append(ExpectResult(
                        is_pass=False, message="Exception {}".format(traceback.format_exc()), node="", val="", expect=""
                    ))
                case_result.step_results.append(step_result)
            test_result.case_results.append(case_result)
        print(reporters["text"].report(test_result))
