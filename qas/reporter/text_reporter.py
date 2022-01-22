#!/usr/bin/env python3
import itertools
import json
import re

import durationpy
from colorama import Fore
from .reporter import Reporter
from ..result import TestResult, CaseResult, StepResult, ExpectResult


class TextReporter(Reporter):
    def __init__(self):
        self.padding = ""

    def report_test_start(self, info):
        print("{}测试 {} 开始".format(self.padding, info["name"]))
        self.padding += "  "

    def report_test_end(self, res: TestResult):
        self.padding = self.padding[:-2]
        if res.is_pass:
            print("{}{}测试 {} 通过，成功 {}，跳过 {}，步骤成功 {}，跳过 {}，断言成功 {}，耗时 {}{}".format(
                self.padding, Fore.GREEN, res.name, res.case_succ, res.case_skip,
                res.step_succ, res.step_skip, res.assertion_succ,
                durationpy.to_str(res.elapse), Fore.RESET,
            ))
        else:
            print("{}{}测试 {} 失败，成功 {}，失败 {}，跳过 {}，步骤成功 {}，失败 {}，断言成功 {}，失败 {}，耗时 {}{}".format(
                self.padding, Fore.RED, res.name, res.case_succ, res.case_fail, res.case_skip,
                res.step_succ, res.step_fail, res.assertion_succ, res.assertion_fail,
                durationpy.to_str(res.elapse), Fore.RESET))

    def report_case_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TextReporter.format_case(res, "case")]))

    def report_skip_case(self, name):
        print("{}{}case {} 跳过{}".format(self.padding, Fore.YELLOW, name, Fore.RESET))

    def report_setup_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TextReporter.format_case(res, "setUp")]))

    def report_teardown_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TextReporter.format_case(res, "tearDown")]))

    @staticmethod
    def format_case(res: CaseResult, case_type: str) -> list[str]:
        lines = []
        if res.is_pass:
            lines.append("{}{} {} 通过，步骤成功 {}，断言成功 {}，耗时 {}{}".format(
                Fore.GREEN, case_type, res.name, res.step_succ, res.assertion_succ,
                durationpy.to_str(res.elapse), Fore.RESET,
            ))
        else:
            lines.append("{}{} {} 失败，步骤成功 {}，失败 {}，断言成功 {}，失败 {}，耗时 {}{}".format(
                Fore.RED, case_type, res.name, res.step_succ, res.step_fail, res.assertion_succ, res.assertion_fail,
                durationpy.to_str(res.elapse), Fore.RESET,
            ))

        for step in res.before_case_steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "beforeCase step")])
        for step in res.preSteps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "case preStep")])
        for step in res.steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "case step")])
        for step in res.postSteps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "case postStep")])
        for step in res.after_case_steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "afterCase step")])

        return lines

    @staticmethod
    def format_step(res, step_type: str) -> list[str]:
        if res.is_skip:
            return ["{}{} {} 跳过{}".format(Fore.YELLOW, step_type, res.name, Fore.RESET)]

        lines = []
        if res.is_pass:
            lines.append("{}{} {} 通过，断言成功 {}，耗时 {}{}".format(
                Fore.GREEN, step_type, res.name, res.assertion_succ, durationpy.to_str(res.elapse), Fore.RESET,
            ))
        else:
            lines.append("{}{} {} 失败，断言成功 {}，失败 {}，耗时 {}{}".format(
                Fore.RED, step_type, res.name, res.assertion_succ, res.assertion_fail, durationpy.to_str(res.elapse), Fore.RESET,
            ))

        lines.extend(("req: " + json.dumps(res.req, indent=True)).split("\n"))

        if res.is_err:
            lines.extend(("res: " + json.dumps(res.res, indent=True)).split("\n"))
            lines.extend(["  " + i for i in res.err.split("\n")])
            return lines

        # 修改 res 返回值，将预期值标记后拼接在 value 后面
        for expect_result in res.assertions:
            if expect_result.is_pass:
                TextReporter.append_val_to_key(res.res, expect_result.node, "<GREEN>{}<END>".format(expect_result.expect))
            else:
                TextReporter.append_val_to_key(res.res, expect_result.node, "<RED>{}<END>".format(expect_result.expect))

        res_lines = ("res: " + json.dumps(res.res, indent=True)).split("\n")
        format_lines = []
        # 解析 res 中 value 的值，重新拼接成带颜色的结果值
        for line in res_lines:
            mr = re.match(r'(\s+".*?": )"(.*)<GREEN>(.*)<END>"(.*)', line)
            if mr:
                format_lines.append(
                    "{}{}{} # {}{}{}".format(mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.GREEN,
                                             mr.groups()[2], Fore.RESET))
                continue
            mr = re.match(r'(\s+".*?": )"(.*)<RED>(.*)<END>"(.*)', line)
            if mr:
                format_lines.append(
                    "{}{}{} # {}{}{}".format(mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.RED,
                                             mr.groups()[2], Fore.RESET))
                continue
            format_lines.append(line)

        lines.extend(format_lines)
        return lines

    @staticmethod
    def append_val_to_key(vals: dict, key, val):
        keys = key.split(".")
        for k in keys[:-1]:
            if isinstance(vals, dict):
                vals = vals[k]
            else:
                vals = vals[int(k)]
        if isinstance(vals, dict):
            vals[keys[-1]] = "{}{}".format(json.dumps(vals[keys[-1]]), val)
        else:
            vals[int(keys[-1])] = "{}{}".format(json.dumps(vals[int(keys[-1])]), val)
