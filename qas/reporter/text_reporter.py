#!/usr/bin/env python3


import json
import re
from colorama import Fore
from ..result import TestResult, CaseResult, StepResult, ExpectResult


class TextReporter:
    def __init__(self):
        self.padding = ""

    def report_test_start(self, info):
        print("{}测试 {} 开始".format(self.padding, info["name"]))
        self.padding += "  "

    def report_test_end(self, res: TestResult):
        self.padding = self.padding[:-2]
        if res.is_pass:
            print("{}{}测试 {} 通过, 成功 {}，失败 {}，跳过 {}{}".format(self.padding, Fore.GREEN, res.name, res.succ, res.fail, res.skip, Fore.RESET))
        else:
            print("{}{}测试 {} 通过, 失败 {}，失败 {}，跳过 {}{}".format(self.padding, Fore.RED, res.name, res.succ, res.fail, res.skip, Fore.RESET))

    def report_case_start(self, case):
        pass

    def report_case_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TextReporter.format_case(res, "case")]))

    def report_setup_start(self, case):
        pass

    def report_setup_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TextReporter.format_case(res, "setUp")]))

    def report_teardown_start(self, result):
        pass

    def report_teardown_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TextReporter.format_case(res, "tearDown")]))

    def report_step_start(self, result):
        pass

    def report_step_end(self, result):
        pass

    @staticmethod
    def format_case(res: CaseResult, case_type: str) -> list[str]:
        lines = []
        if res.is_pass:
            lines.append(Fore.GREEN + "{} {} 通过".format(case_type, res.case) + Fore.RESET)
        else:
            lines.append(Fore.RED + "{} {} 失败".format(case_type, res.case) + Fore.RESET)
        for step_result in res.steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step_result)])
        return lines

    @staticmethod
    def format_step(res) -> list[str]:
        lines = []
        if res.is_pass:
            lines.append(Fore.GREEN + "step {} 通过".format(res.step) + Fore.RESET)
        else:
            lines.append(Fore.RED + "step {} 失败".format(res.step) + Fore.RESET)

        lines.extend(("req: " + json.dumps(res.req, indent=True)).split("\n"))

        if res.is_err:
            lines.extend(("res: " + json.dumps(res.res, indent=True)).split("\n"))
            lines.extend(["  " + i for i in res.err.split("\n")])
            return lines

        # 修改 res 返回值，将预期值标记后拼接在 value 后面
        for expect_result in res.expects:
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
        vals[keys[-1]] = "{}{}".format(json.dumps(vals[keys[-1]]), val)
