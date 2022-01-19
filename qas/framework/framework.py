#!/usr/bin/env python3


import copy
import re
import time
import yaml
import traceback
import os
import json
from types import SimpleNamespace
from datetime import datetime, timedelta

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

    def exec_directory(self, test_directory, parent_var_info, parent_ctx, parent_dft_info, parent_before_case_info, parent_after_case_info):
        now = datetime.now()
        self._debug("enter {}".format(test_directory))

        info = Framework.load_ctx(os.path.basename(test_directory), "{}/ctx.yaml".format(test_directory))
        var_info = copy.deepcopy(parent_var_info) | info["var"]
        var = json.loads(json.dumps(var_info), object_hook=dict_to_sns)
        before_case_info = copy.deepcopy(parent_before_case_info) + info["beforeCase"] + list(Framework.load_step("{}/before_case.yaml".format(test_directory)))
        after_case_info = copy.deepcopy(parent_after_case_info) + info["afterCase"] + list(Framework.load_step("{}/after_case.yaml".format(test_directory)))
        ctx = copy.copy(parent_ctx)
        dft_info = copy.deepcopy(parent_dft_info)
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
            val = render(val, var=var)
            ctx[key] = drivers[val["type"]](val["args"])
            dft_info[key] = val["dft"]

        self._debug("var: {}".format(var_info))
        self._debug("ctx: {}".format(ctx))
        self._debug("req: {}".format(dft_info))

        test_result = TestResult(info["name"])
        self.reporter.report_test_start(info)

        # 执行 setup
        if not self.skip_setup:
            for case_info in self.teardowns(info, test_directory):
                self.reporter.report_setup_start(case_info)
                result = self.run_case(before_case_info, case_info, after_case_info, dft_info, var=var, ctx=ctx, skip_hook=True)
                test_result.setups.append(result)
                self.reporter.report_setup_end(result)
                if not result.is_pass:
                    test_result.is_pass = False
                    self.reporter.report_test_end(test_result)
                    return test_result

        # 执行 case
        for case_info in self.cases(info, test_directory):
            if self.need_skip(case_info, var):
                test_result.skip += 1
                continue
            self.reporter.report_case_start(case_info)
            result = self.run_case(before_case_info, case_info, after_case_info, dft_info, var=var, ctx=ctx)
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
            sub_test_result = self.exec_directory(directory, var_info, ctx, dft_info, before_case_info, after_case_info)
            test_result.sub_tests.append(sub_test_result)
            test_result.succ += sub_test_result.succ
            test_result.fail += sub_test_result.fail
            test_result.skip += sub_test_result.skip

        test_result.is_pass = test_result.fail == 0

        # 执行 teardown
        if not self.skip_teardown:
            for case_info in self.teardowns(info, test_directory):
                self.reporter.report_teardown_start(case_info)
                result = self.run_case(before_case_info, case_info, after_case_info, dft_info, var=var, ctx=ctx, skip_hook=True)
                test_result.teardowns.append(result)
                self.reporter.report_teardown_end(result)
                if not result.is_pass:
                    test_result.is_pass = False
                    self.reporter.report_test_end(test_result)
                    return test_result

        test_result.elapse = datetime.now() - now
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

    def run_case(self, before_case_info, case_info, after_case_info, dft, var=None, ctx=None, skip_hook=False):
        case = CaseResult(case_info["name"])

        now = datetime.now()
        if not skip_hook:
            for idx, step_info in enumerate(before_case_info):
                step = self.run_step("step-{}".format(idx), step_info, case, dft, var=var, ctx=ctx)
                case.before_steps.append(step)
                if not step.is_pass:
                    break
                self.reporter.report_step_end(step)

        for idx, step_info in enumerate(case_info["step"]):
            step = self.run_step("step-{}".format(idx), step_info, case, dft, var=var, ctx=ctx)
            case.steps.append(step)
            if not step.is_pass:
                break
            self.reporter.report_step_end(step)

        if not skip_hook:
            for idx, step_info in enumerate(after_case_info):
                step = self.run_step("step-{}".format(idx), step_info, case, dft, var=var, ctx=ctx)
                case.after_steps.append(step)
                if not step.is_pass:
                    break
                self.reporter.report_step_end(step)

        case.elapse = datetime.now() - now
        case.summary()
        return case

    def run_step(self, dft_step_name, step_info, case, dft, var=None, ctx=None):
        step_info = merge(step_info, {
            "name": dft_step_name,
            "res": {},
            "retry": {},
            "until": {},
        })

        self._debug("step {}".format(json.dumps(step_info, indent=True)))

        step = StepResult(step_info["name"])
        now = datetime.now()
        self.reporter.report_step_start(step_info)
        try:
            req = merge(step_info["req"], dft[step_info["ctx"]]["req"])
            req = render(req, case=case, var=var)
            step.req = req

            retry = Retry(merge(step_info["retry"], dft[step_info["ctx"]]["retry"]))
            until = Until(merge(step_info["until"], dft[step_info["ctx"]]["until"]))

            for i in range(until.attempts):
                for j in range(retry.attempts):
                    res = ctx[step_info["ctx"]].do(req)
                    step.res = res
                    if retry.condition == "" or not expect_val(None, retry.condition, case=case, step=step, var=var):
                        break
                    time.sleep(retry.delay.total_seconds())
                else:
                    raise RetryError()
                if until.condition == "" or expect_val(None, until.condition, case=case, step=step, var=var):
                    break
                time.sleep(until.delay.total_seconds())
            else:
                raise UntilError()

            result = expect(res, step_info["res"], case=case, step=step, var=var)
            step.expects.extend(result)
        except RetryError as e:
            step.set_error("RetryError [{}]".format(retry))
        except UntilError as e:
            step.set_error("UntilError [{}], ".format(until))
        except Exception as e:
            step.set_error("Exception {}".format(traceback.format_exc()))

        step.elapse = datetime.now() - now
        step.summary()
        return step

    def _debug(self, message):
        if self.debug:
            print("### ", message)
