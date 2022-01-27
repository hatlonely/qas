#!/usr/bin/env python3


import copy
import itertools
import re
import time
import yaml
import traceback
import os
import json
import importlib
import sys
from types import SimpleNamespace
from datetime import datetime

from ..driver import HttpDriver, POPDriver, OTSDriver, ShellDriver, MysqlDriver, RedisDriver, MNSDriver, OSSDriver, MongoDriver, merge, REQUIRED
from ..assertion import expect, render, expect_val
from ..result import TestResult, CaseResult, StepResult
from ..reporter import TextReporter, JsonReporter
from .retry_until import Retry, Until, RetryError, UntilError
from .generate import generate_req, generate_res, calculate_num


sys.path.append(".")


def dict_to_sns(d):
    return SimpleNamespace(**d)


_drivers = {
    "http": HttpDriver,
    "redis": RedisDriver,
    "shell": ShellDriver,
    "mysql": MysqlDriver,
    "mongo": MongoDriver,
    "pop": POPDriver,
    "ots": OTSDriver,
    "mns": MNSDriver,
    "oss": OSSDriver,
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
    debug_mode: bool

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
        self.debug_mode = debug
        self.reporter = reporters[reporter]()

    def run(self):
        res = self.run_test(self.test_directory, {}, {}, {}, {}, [], [], _drivers)
        return res.is_pass

    def run_test(
            self,
            test_directory,
            parent_var_info,
            parent_ctx,
            parent_dft_info,
            parent_common_step_info,
            parent_before_case_info,
            parent_after_case_info,
            parent_drivers,
    ):
        now = datetime.now()
        self.debug("enter {}".format(test_directory))

        drivers = parent_drivers | Framework.load_driver("{}/qas".format(test_directory))
        info = Framework.load_ctx(os.path.basename(test_directory), "{}/ctx.yaml".format(test_directory))
        var_info = copy.deepcopy(parent_var_info) | info["var"] | Framework.load_var("{}/var.yaml".format(test_directory))
        var = json.loads(json.dumps(var_info), object_hook=dict_to_sns)
        common_step_info = copy.deepcopy(parent_common_step_info) | info["commonStep"] | Framework.load_common_step("{}/common_step.yaml".format(test_directory))
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

        self.debug("var: {}".format(var_info))
        self.debug("ctx: {}".format(ctx))
        self.debug("req: {}".format(dft_info))

        test_result = TestResult(info["name"])
        self.reporter.report_test_start(info)

        # 执行 setup
        if not self.skip_setup:
            for case_info in self.setups(info, test_directory):
                self.reporter.report_setup_start(case_info)
                result = self.run_case([], case_info, [], {}, dft_info, var=var, ctx=ctx)
                test_result.add_setup_result(result)
                self.reporter.report_setup_end(result)
                if not result.is_pass:
                    self.reporter.report_test_end(test_result)
                    return test_result

        # 执行 case
        for case_info in self.cases(info, test_directory):
            if self.need_skip(case_info, var):
                test_result.skip_case(case_info["name"])
                self.reporter.report_skip_case(case_info["name"])
                continue
            self.reporter.report_case_start(case_info)
            result = self.run_case(before_case_info, case_info, after_case_info, common_step_info, dft_info, var=var, ctx=ctx)
            test_result.add_case_result(result)
            self.reporter.report_case_end(result)

        # 执行子目录
        for directory in [
            os.path.join(test_directory, i)
            for i in os.listdir(test_directory)
            if i != "qas" and os.path.isdir(os.path.join(test_directory, i))
        ]:
            if self.case_directory and not re.search(self.case_directory, directory):
                continue
            sub_test_result = self.run_test(directory, var_info, ctx, dft_info, common_step_info, before_case_info, after_case_info, drivers)
            test_result.add_sub_test_result(sub_test_result)

        # 执行 teardown
        if not self.skip_teardown:
            for case_info in self.teardowns(info, test_directory):
                self.reporter.report_teardown_start(case_info)
                result = self.run_case([], case_info, [], {}, dft_info, var=var, ctx=ctx)
                test_result.teardowns.append(result)
                self.reporter.report_teardown_end(result)
                if not result.is_pass:
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
        if "cond" in case and case["cond"] and not expect_val(None, case["cond"], var=var):
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
            if i not in ["var.yaml", "ctx.yaml", "setup.yaml", "teardown.yaml", "before_case.yaml", "after_case.yaml", "common_step.yaml"]
            and os.path.isfile(os.path.join(test_directory, i))
        ]:
            if not filename.endswith(".yaml"):
                continue
            for case in self.load_case(filename):
                yield case

    @staticmethod
    def load_driver(filename):
        if not os.path.exists(filename) or not os.path.isdir(filename):
            return {}
        return importlib.import_module(filename.replace("/", "."), "custom").drivers

    @staticmethod
    def load_var(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return {}
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
        return info

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
            "afterCase": [],
            "commonStep": {},
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
        })
        info["name"] = "{}/{}".format(filename, info["name"])
        return info

    @staticmethod
    def load_step(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return []
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if not info:
                return []
            for step in info:
                yield step

    @staticmethod
    def load_common_step(filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return {}
        with open(filename, "r", encoding="utf-8") as fp:
            info = yaml.safe_load(fp)
            if not info:
                return {}
        return info

    def run_case(self, before_case_info, case_info, after_case_info, common_step_info, dft, var=None, ctx=None):
        case_info = merge(case_info, {
            "name": REQUIRED,
            "cond": "",
            "label": {},
            "preStep": [],
            "postStep": [],
        })

        case = CaseResult(case_info["name"])

        now = datetime.now()
        for idx, step_info, case_add_step_func, case_skip_step_func in itertools.chain(
            [list(i) + [case.add_before_case_step_result, case.skip_before_case_step] for i in enumerate(before_case_info)],
            [list(i) + [case.add_case_pre_step_result, case.skip_case_step] for i in enumerate([common_step_info[i] for i in case_info["preStep"]])],
            [list(i) + [case.add_case_step_result, case.skip_case_step] for i in enumerate(case_info["step"])],
            [list(i) + [case.add_case_post_step_result, case.skip_case_step] for i in enumerate([common_step_info[i] for i in case_info["postStep"]])],
            [list(i) + [case.add_after_case_step_result, case.skip_after_case_step] for i in enumerate(after_case_info)],
        ):
            step_info = merge(step_info, {
                "name": "step-{}".format(idx),
                "res": {},
                "retry": {},
                "until": {},
                "cond": "",
            })

            # 条件步骤
            if step_info["cond"] and not expect_val(None, step_info["cond"], case=case, var=var):
                case_skip_step_func(step_info["name"])
                self.reporter.report_skip_step(step_info["name"])
                continue
            step = self.run_step(step_info, case, dft, var=var, ctx=ctx)
            case_add_step_func(step)
            self.reporter.report_step_end(step)
            if not step.is_pass:
                break

        case.elapse = datetime.now() - now
        return case

    def run_step(self, step_info, case, dft, var=None, ctx=None):
        self.debug("step {}".format(json.dumps(step_info, indent=True)))

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
            step.add_expect_result(result)
        except RetryError as e:
            step.set_error("RetryError [{}]".format(retry))
        except UntilError as e:
            step.set_error("UntilError [{}], ".format(until))
        except Exception as e:
            step.set_error("Exception {}".format(traceback.format_exc()))

        step.elapse = datetime.now() - now
        return step

    def debug(self, message):
        if self.debug_mode:
            print("### ", message)
