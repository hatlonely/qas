#!/usr/bin/env python3


import json
import re
from colorama import Fore
from ..result import TestResult, CaseResult, StepResult, ExpectResult


class TextReporter:
    @staticmethod
    def report(res: TestResult) -> str:
        res.summary()
        return '\n'.join(TextReporter.test_summary(res))

    @staticmethod
    def test_summary(res: TestResult) -> list[str]:
        lines = []
        if res.is_pass:
            lines.append(Fore.GREEN + "测试通过, 成功 {}".format(res.succ) + Fore.RESET)
        else:
            lines.append(Fore.RED + "测试失败，成功 {}，失败 {}".format(res.succ, res.fail) + Fore.RESET)

        for cs in res.setups:
            lines.extend(["  " + i for i in TextReporter.case_summary(cs)])
        for cs in res.cases:
            lines.extend(["  " + i for i in TextReporter.case_summary(cs)])
        for cs in res.teardowns:
            lines.extend(["  " + i for i in TextReporter.case_summary(cs)])
        return lines

    @staticmethod
    def case_summary(res: CaseResult) -> list[str]:
        lines = []
        if res.is_pass:
            lines.append(Fore.GREEN + "case {} 通过".format(res.case) + Fore.RESET)
        else:
            lines.append(Fore.RED + "case {} 失败".format(res.case) + Fore.RESET)
        for step_result in res.steps:
            lines.extend(["  " + i for i in TextReporter.step_summary(step_result)])
        return lines

    @staticmethod
    def step_summary(res: StepResult) -> list[str]:
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
                format_lines.append("{}{}{} # {}{}{}".format(mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.GREEN, mr.groups()[2], Fore.RESET))
                continue
            mr = re.match(r'(\s+".*?": )"(.*)<RED>(.*)<END>"(.*)', line)
            if mr:
                format_lines.append("{}{}{} # {}{}{}".format(mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.RED, mr.groups()[2], Fore.RESET))
                continue
            format_lines.append(line)

        lines.extend(format_lines)

        return lines

    @staticmethod
    def expect_summary(res: ExpectResult) -> str:
        if res.is_pass:
            return "node [{}] {}".format(res.node, res.message)
        else:
            return Fore.RED + "node [{}] {}. val: {}, expect: {}".format(res.node, res.message, res.val, res.expect) + Fore.RESET

    @staticmethod
    def append_val_to_key(vals: dict, key, val):
        keys = key.split(".")
        for k in keys[:-1]:
            if isinstance(vals, dict):
                vals = vals[k]
            else:
                vals = vals[int(k)]
        vals[keys[-1]] = "{}{}".format(json.dumps(vals[keys[-1]]), val)
