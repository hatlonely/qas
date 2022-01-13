#!/usr/bin/env python3

import yaml
from src.qas.driver.http_driver import HttpDriver
from src.qas.driver.pop_driver import POPDriver
from src.qas.assertion.expect import expect_obj
from src.qas.assertion.expect import TestResult, CaseResult, StepResult
from src.qas.reporter.text_reporter import report


drivers = {
    "http": HttpDriver,
    "pop": POPDriver,
}


class Framework:
    data = None
    case = None
    name = None
    ctx = dict()

    def __init__(self, filename):
        fp = open(filename, "r", encoding="utf-8")
        data = yaml.safe_load(fp)
        self.data = data
        self.case = data["case"]
        self.name = data["name"]
        for key in data["ctx"]:
            val = data["ctx"][key]
            self.ctx[key] = drivers[val["type"]](val["args"])

    def run(self):
        test_result = TestResult(self.name)
        for case in self.case:
            case_result = CaseResult(case["name"])
            for idx, step in enumerate(case["step"]):
                if "name" not in step:
                    step["name"] = "step-{}".format(idx)
                step_result = StepResult(step["name"])
                res = self.ctx[step["ctx"]].do(step["req"])
                res = expect_obj(res, step["res"])
                step_result.expect_results.extend(res)
                case_result.step_results.append(step_result)
            test_result.case_results.append(case_result)
        print(report(test_result))
