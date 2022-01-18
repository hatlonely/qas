#!/usr/bin/env python3
import copy
import re

import yaml
import traceback
import os
import json
from types import SimpleNamespace

from ..driver import HttpDriver, POPDriver, OTSDriver, ShellDriver, MysqlDriver, merge, REQUIRED
from ..assertion import expect, render, expect_val
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
    # "json": JsonReporter,
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
        self.exec_directory(self.test_directory, {}, {}, {})

    def need_skip(self, case, var):
        if self.case_name and self.case_name != case["name"]:
            return True
        if self.case_regex and not re.search(self.case_regex, case["name"]):
            return True
        if case["cond"] and not expect_val(None, case["cond"], case, var):
            return True
        return False

    def exec_directory(self, test_directory, parent_var, parent_ctx, parent_req):
        info = Framework.load_ctx(os.path.basename(test_directory), "{}/ctx.yaml".format(test_directory))
        var = copy.deepcopy(parent_var) | info["var"]
        ctx = copy.copy(parent_ctx)
        req = copy.copy(parent_req)

        var_namespace = json.loads(json.dumps(var), object_hook=dict_to_sns)
        for key in info["ctx"]:
            val = merge(info["ctx"][key], {
                "type": REQUIRED,
                "args": {},
                "req": {},
            })
            val = render(val, var=var_namespace)
            ctx[key] = drivers[val["type"]](val["args"])
            req[key] = val["req"]

        test_result = TestResult(info["name"])
        self.reporter.report_test_start(info)

        # 执行 setup
        if not self.skip_setup:
            for case in info["setUp"]:
                self.reporter.report_setup_start(case)
                result = self.run_case(case, var_namespace, ctx, req)
                test_result.setups.append(result)
                self.reporter.report_setup_end(result)
                if not result.is_pass:
                    test_result.is_pass = False
                    self.reporter.report_test_end(test_result)
                    return test_result
            if os.path.isfile("{}/setup.yaml".format(test_directory)):
                for case in self.load_case("{}/setup.yaml".format(test_directory)):
                    self.reporter.report_setup_start(case)
                    result = self.run_case(case, var_namespace, ctx, req)
                    test_result.setups.append(result)
                    self.reporter.report_setup_end(result)
                    if not result.is_pass:
                        test_result.is_pass = False
                        self.reporter.report_test_end(test_result)
                        return test_result

        for case in info["case"]:
            if self.need_skip(case, var_namespace):
                test_result.skip += 1
                continue
            self.reporter.report_case_start(case)
            result = self.run_case(case, var_namespace, ctx, req)
            test_result.cases.append(result)
            self.reporter.report_case_end(result)
            if result.is_pass:
                test_result.succ += 1
            else:
                test_result.fail += 1

        # 执行文件中的 case
        for filename in [
            os.path.join(test_directory, i)
            for i in os.listdir(test_directory)
            if i not in ["ctx.yaml", "setup.yaml", "teardown.yaml"] and os.path.isfile(os.path.join(test_directory, i))
        ]:
            for case in self.load_case(filename):
                if self.need_skip(case, var_namespace):
                    test_result.skip += 1
                    continue
                self.reporter.report_case_start(case)
                result = self.run_case(case, var_namespace, ctx, req)
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
            sub_test_result = self.exec_directory(directory, var, ctx, req)
            test_result.sub_tests.append(sub_test_result)
            test_result.succ += sub_test_result.succ
            test_result.fail += sub_test_result.fail
            test_result.skip += sub_test_result.skip

        if not self.skip_teardown:
            for case in info["tearDown"]:
                self.reporter.report_teardown_start(case)
                result = self.run_case(case, var_namespace, ctx, req)
                test_result.teardowns.append(result)
                self.reporter.report_teardown_end(result)
                if not result.is_pass:
                    test_result.is_pass = False
                    self.reporter.report_test_end(test_result)
                    return test_result
            if os.path.isfile("{}/teardown.yaml".format(test_directory)):
                for case in self.load_case("{}/teardown.yaml".format(test_directory)):
                    self.reporter.report_teardown_start(case)
                    result = self.run_case(case, var_namespace, ctx, req)
                    test_result.teardowns.append(result)
                    self.reporter.report_teardown_end(result)
                    if not result.is_pass:
                        test_result.is_pass = False
                        self.reporter.report_test_end(test_result)
                        return test_result

        test_result.is_pass = test_result.fail == 0
        # 执行 teardown
        self.reporter.report_test_end(test_result)
        return test_result

    @staticmethod
    def load_ctx(name, filename):
        dft = {
            "name": name,
            "ctx": {},
            "var": {},
            "case": [],
            "setUp": [],
            "tearDown": [],
        }
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return dft
        fp = open(filename, "r", encoding="utf-8")
        info = yaml.safe_load(fp)
        fp.close()
        return merge(info, dft)

    @staticmethod
    def load_case(filename):
        fp = open(filename, "r", encoding="utf-8")
        info = yaml.safe_load(fp)
        fp.close()
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

    def run_case(self, case, var, ctx, req):
        case_result = CaseResult(case["name"])
        for idx, step in enumerate(case["step"]):
            step = merge(step, {
                "name": "step-{}".format(idx),
                "res": {},
            })
            step_result = StepResult(step["name"])
            self.reporter.report_step_start(step)
            try:
                req = merge(step["req"], req[step["ctx"]])
                req = render(req, case=case_result, var=var)
                step_result.req = req
                res = ctx[step["ctx"]].do(req)
                step_result.res = res
                result = expect(res, step["res"], case=case_result, var=var)
                step_result.expects.extend(result)
            except Exception as e:
                step_result.is_err = True
                step_result.err = "Exception {}".format(traceback.format_exc())
                step_result.is_pass = False
            case_result.steps.append(step_result)
            step_result.summary()
            if not step_result.is_pass:
                break
            self.reporter.report_step_end(step_result)
        case_result.summary()
        return case_result



# class Framework2:
#     data = None
#     case = None
#     name = None
#     set_up = None
#     tear_down = None
#     ctx = dict()
#     var = dict()
#     req = dict()
#     case_name = None
#     case_regex = None
#     skip_setup = False
#     skip_teardown = False
#
#     def __init__(self, test_directory, case_directory=None, case_name=None, case_regex=None, skip_setup=False, skip_teardown=False):
#         self.case_name = case_name
#         self.case_regex = case_regex
#         self.skip_setup = skip_setup
#         self.skip_teardown = skip_teardown
#         if os.path.isfile(test_directory):
#             self.load_ctx(test_directory)
#             return
#
#         # load ctx.yaml
#         self.load_ctx("{}/ctx.yaml".format(test_directory))
#         case_parent_directory = "{}/cases".format(test_directory)
#         if case_directory:
#             dirs = case_directory.split("")
#         else:
#             dirs = [i for i in os.listdir(case_parent_directory) if os.path.isdir(os.path.join(case_parent_directory, i))]
#         for cd in dirs:
#             for filename in os.listdir("{}/{}".format(case_parent_directory, cd)):
#                 for c in self.load_case("{}/cases/{}/{}".format(test_directory, cd, filename)):
#                     self.case.append(c)
#
#         if os.path.isfile("{}/setup.yaml".format(test_directory)):
#             for c in self.load_case("{}/setup.yaml".format(test_directory)):
#                 self.set_up.append(c)
#
#         if os.path.isfile("{}/teardown.yaml".format(test_directory)):
#             for c in self.load_case("{}/teardown.yaml".format(test_directory)):
#                 self.tear_down.append(c)
#
#     def load_ctx(self, ctx_filename):
#         if not os.path.exists(ctx_filename) or not os.path.isfile(ctx_filename):
#             raise Exception("ctx file [{}] is missing".format(ctx_filename))
#         fp = open(ctx_filename, "r", encoding="utf-8")
#         data = yaml.safe_load(fp)
#         fp.close()
#         data = merge(data, {
#             "name": REQUIRED,
#             "ctx": REQUIRED,
#             "var": {},
#             "case": [],
#             "setUp": [],
#             "tearDown": [],
#         })
#         self.data = data
#         self.var = json.loads(json.dumps(data["var"]), object_hook=dict_to_sns)
#         self.name = data["name"]
#         for key in data["ctx"]:
#             val = merge(data["ctx"][key], {
#                 "type": REQUIRED,
#                 "args": {},
#                 "req": {},
#             })
#             val = render(val, var=self.var)
#             self.ctx[key] = drivers[val["type"]](val["args"])
#             self.req[key] = val["req"]
#         self.case = data["case"]
#         self.set_up = data["setUp"]
#         self.tear_down = data["tearDown"]
#
#     def load_case(self, filename):
#         fp = open(filename, "r", encoding="utf-8")
#         data = yaml.safe_load(fp)
#         fp.close()
#         if isinstance(data, dict):
#             yield self.format_case(filename, data)
#         if isinstance(data, list):
#             for item in data:
#                 yield self.format_case(filename, item)
#
#     def format_case(self, filename, data):
#         data = merge(data, {
#             "name": REQUIRED,
#             "cond": "",
#             "label": {},
#         })
#         data["name"] = "{}/{}".format(filename, data["name"])
#         return data
#
#     def run(self):
#         result = self.run_all_cases()
#         result.summary()
#         print(reporters["text"].report(result))
#         return result.is_pass
#
#     def run_all_cases(self):
#         test_result = TestResult(self.name)
#         if not self.skip_setup:
#             for case in self.set_up:
#                 result = self.run_case(case)
#                 test_result.setups.append(result)
#                 if not result.is_pass:
#                     test_result.is_pass = False
#                     return test_result
#         for case in self.case:
#             if self.case_name and self.case_name != case["name"]:
#                 test_result.skip += 1
#                 continue
#             if self.case_regex and not re.search(self.case_regex, case["name"]):
#                 test_result.skip += 1
#                 continue
#             if case["cond"] and not expect_val(None, case["cond"], case, self.var):
#                 test_result.skip += 1
#                 continue
#             test_result.cases.append(self.run_case(case))
#         if not self.skip_teardown:
#             for case in self.tear_down:
#                 test_result.teardowns.append(self.run_case(case))
#         return test_result
#
#     def run_case(self, case):
#         case_result = CaseResult(case["name"])
#         for idx, step in enumerate(case["step"]):
#             step = merge(step, {
#                 "name": "step-{}".format(idx),
#                 "res": {},
#             })
#             step_result = StepResult(step["name"])
#             try:
#                 req = merge(step["req"], self.req[step["ctx"]])
#                 req = render(req, case=case_result, var=self.var)
#                 step_result.req = req
#                 res = self.ctx[step["ctx"]].do(req)
#                 step_result.res = res
#                 result = expect(res, step["res"], case=case_result, var=self.var)
#                 step_result.expects.extend(result)
#             except Exception as e:
#                 step_result.is_err = True
#                 step_result.err = "Exception {}".format(traceback.format_exc())
#                 step_result.is_pass = False
#             case_result.steps.append(step_result)
#             step_result.summary()
#             if not step_result.is_pass:
#                 break
#         case_result.summary()
#         return case_result
