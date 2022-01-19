#!/usr/bin/env python3


import copy
import re
import time

import yaml
import traceback
import os
import json
from types import SimpleNamespace

from ..driver import HttpDriver, POPDriver, OTSDriver, ShellDriver, MysqlDriver, merge, REQUIRED
from ..assertion import expect, render, expect_val
from ..result import TestResult, CaseResult, StepResult
from ..reporter import TextReporter, JsonReporter
from .retry_until import Retry, Until, RetryError, UntilError


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
    test_directory: str
    case_directory: str
    case_regex: str
    case_name: str
    skip_setup: bool
    skip_teardown: bool
    debug: bool

    def __init__(
        self,
        test_directory,
        case_directory=None,
        case_name=None,
        case_regex=None,
        skip_setup=False,
        skip_teardown=False,
        debug=False,
        reporter="text",
    ):
        self.test_directory = test_directory
        self.case_directory = case_directory
        self.case_regex = case_regex
        self.case_name = case_name
        self.skip_setup = skip_setup
        self.skip_teardown = skip_teardown
        self.debug = debug
        self.reporter = reporters[reporter]()

    def run(self):
        res = self.exec_directory(self.test_directory, {}, {}, {}, [], [])
        return res.is_pass

    def exec_directory(self, test_directory, parent_var, parent_ctx, parent_dft, parent_before_case, parent_after_case):
        self._debug("enter {}".format(test_directory))

        info = Framework.load_ctx(os.path.basename(test_directory), "{}/ctx.yaml".format(test_directory))
        var = copy.deepcopy(parent_var) | info["var"]
        var_namespace = json.loads(json.dumps(var), object_hook=dict_to_sns)
        before_case = copy.deepcopy(parent_before_case) + info["beforeCase"] + list(Framework.load_step("{}/before_case.yaml".format(test_directory)))
        after_case = copy.deepcopy(parent_after_case) + info["afterCase"] + list(Framework.load_step("{}/after_case.yaml".format(test_directory)))
        ctx = copy.copy(parent_ctx)
        dft = copy.deepcopy(parent_dft)
        for key in info["ctx"]:
            val = merge(info["ctx"][key], {
                "type": REQUIRED,
                "args": {},
                "dft": {
                    "req": {},
                    "retry": {
                        "attempts": 1,
                        "delay": "1s",
                    },
                    "until": {
                        "cond": "",
                        "attempts": 5,
                        "delay": "1s",
                    },
                },
            })
            val = render(val, var=var_namespace)
            ctx[key] = drivers[val["type"]](val["args"])
            dft[key] = val["dft"]

        self._debug("var: {}".format(var))
        self._debug("ctx: {}".format(ctx))
        self._debug("req: {}".format(dft))

        test_result = TestResult(info["name"])
        self.reporter.report_test_start(info)

        # 执行 setup
        if not self.skip_setup:
            for case in self.teardowns(info, test_directory):
                self.reporter.report_setup_start(case)
                result = self.run_case(before_case, case, after_case, var_namespace, ctx, dft)
                test_result.setups.append(result)
                self.reporter.report_setup_end(result)
                if not result.is_pass:
                    test_result.is_pass = False
                    self.reporter.report_test_end(test_result)
                    return test_result

        # 执行 case
        for case in self.cases(info, test_directory):
            if self.need_skip(case, var_namespace):
                test_result.skip += 1
                continue
            self.reporter.report_case_start(case)
            result = self.run_case(before_case, case, after_case, var_namespace, ctx, dft)
            test_result.cases.append(result)
            self.reporter.report_case_end(result)
            if result.is_pass:
                test_result.succ += 1
            else:
                test_result.fail += 1

        # 执行子目录
        for directory in [
            os.path.join(test_directory, i)
            for i in os.listdir(test_directory)
            if os.path.isdir(os.path.join(test_directory, i))
        ]:
            sub_test_result = self.exec_directory(directory, var, ctx, dft, before_case, after_case)
            test_result.sub_tests.append(sub_test_result)
            test_result.succ += sub_test_result.succ
            test_result.fail += sub_test_result.fail
            test_result.skip += sub_test_result.skip

        test_result.is_pass = test_result.fail == 0

        # 执行 teardown
        if not self.skip_teardown:
            for case in self.teardowns(info, test_directory):
                self.reporter.report_teardown_start(case)
                result = self.run_case(before_case, case, after_case, var_namespace, ctx, dft)
                test_result.teardowns.append(result)
                self.reporter.report_teardown_end(result)
                if not result.is_pass:
                    test_result.is_pass = False
                    self.reporter.report_test_end(test_result)
                    return test_result

        self.reporter.report_test_end(test_result)
        return test_result

    def need_skip(self, case, var):
        if self.case_name and self.case_name != case["name"]:
            return True
        if self.case_regex and not re.search(self.case_regex, case["name"]):
            return True
        if case["cond"] and not expect_val(None, case["cond"], var=var):
            return True
        return False

    def setups(self, info, test_directory):
        for case in info["setUp"]:
            yield case
        if os.path.isfile("{}/setup.yaml".format(test_directory)):
            for case in self.load_case("{}/setup.yaml".format(test_directory)):
                yield case

    def teardowns(self, info, test_directory):
        for case in info["tearDown"]:
            yield case
        if os.path.isfile("{}/teardown.yaml".format(test_directory)):
            for case in self.load_case("{}/teardown.yaml".format(test_directory)):
                yield case

    def cases(self, info, test_directory):
        for case in info["case"]:
            yield case

        # 执行文件中的 case
        for filename in [
            os.path.join(test_directory, i)
            for i in os.listdir(test_directory)
            if i not in ["ctx.yaml", "setup.yaml", "teardown.yaml", "before_case.yaml, after_case.yaml"]
            and os.path.isfile(os.path.join(test_directory, i))
        ]:
            for case in self.load_case(filename):
                yield case

    @staticmethod
    def load_ctx(name, filename):
        dft = {
            "name": name,
            "ctx": {},
            "var": {},
            "case": [],
            "setUp": [],
            "tearDown": [],
            "beforeCase": [],
            "afterCase": []
        }
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return dft
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
        return merge(info, dft)

    @staticmethod
    def load_case(filename):
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if isinstance(info, dict):
                yield Framework.format_case(filename, info)
            if isinstance(info, list):
                for item in info:
                    yield Framework.format_case(filename, item)

    @staticmethod
    def format_case(filename, info):
        info = merge(info, {
            "name": REQUIRED,
            "cond": "",
            "label": {},
        })
        info["name"] = "{}/{}".format(filename, info["name"])
        return info

    @staticmethod
    def load_step(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return []
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            for step in info:
                yield step

    def run_case(self, before_case, case, after_case, var, ctx, dft):
        case_result = CaseResult(case["name"])
        for idx, step in enumerate(case["step"]):
            step = merge(step, {
                "name": "step-{}".format(idx),
                "res": {},
                "retry": {},
                "until": {},
            })
            self._debug("step {}".format(json.dumps(step, indent=True)))
            step_result = StepResult(step["name"])
            self.reporter.report_step_start(step)
            try:
                req = merge(step["req"], dft[step["ctx"]]["req"])
                req = render(req, case=case_result, var=var)
                step_result.req = req

                retry = Retry(merge(step["retry"], dft[step["ctx"]]["retry"]))
                until = Until(merge(step["until"], dft[step["ctx"]]["until"]))

                for i in range(until.attempts):
                    for j in range(retry.attempts):
                        res = ctx[step["ctx"]].do(req)
                        step_result.res = res
                        if retry.condition == "" or not expect_val(None, retry.condition, case=case_result, step=step_result, var=var):
                            break
                        time.sleep(retry.delay.total_seconds())
                    else:
                        raise RetryError()
                    if until.condition == "" or expect_val(None, until.condition, case=case_result, step=step_result, var=var):
                        break
                    time.sleep(until.delay.total_seconds())
                else:
                    raise UntilError()

                result = expect(res, step["res"], case=case_result, step=step_result, var=var)
                step_result.expects.extend(result)
            except RetryError as e:
                step_result.set_error("RetryError [{}]".format(retry))
            except UntilError as e:
                step_result.set_error("UntilError [{}], ".format(until))
            except Exception as e:
                step_result.set_error("Exception {}".format(traceback.format_exc()))
            step_result.summary()

            case_result.steps.append(step_result)
            if not step_result.is_pass:
                break
            self.reporter.report_step_end(step_result)
        case_result.summary()
        return case_result

    def run_step(self, info, case, step, var):
        pass

    def _debug(self, message):
        if self.debug:
            print("### ", message)
