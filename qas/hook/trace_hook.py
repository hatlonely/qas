#!/usr/bin/env python3


import json
import re

import durationpy
from colorama import Fore
from .hook import Hook
from ..result import TestResult, CaseResult


class TraceHook(Hook):
    def __init__(self):
        self.padding = ""

    def on_test_start(self, directory):
        print("{}进入 {}".format(self.padding, directory))
        self.padding += "  "

    def on_test_end(self, res: TestResult):
        self.padding = self.padding[:-2]
        if res.is_pass:
            print("{}{}测试 {} 通过，成功 {}，跳过 {}，步骤成功 {}，跳过 {}，断言成功 {}，耗时 {}{}".format(
                self.padding, Fore.GREEN, res.name, res.case_succ, res.case_skip,
                res.step_succ, res.step_skip, res.assertion_succ,
                durationpy.to_str(res.elapse), Fore.RESET,
            ))
        else:
            if res.is_err:
                print('\n'.join([
                    "  {}  {}".format(self.padding, line)
                    for line in res.err.split("\n")
                ]))
            print("{}{}测试 {} 失败，成功 {}，失败 {}，跳过 {}，步骤成功 {}，失败 {}，断言成功 {}，失败 {}，耗时 {}{}".format(
                self.padding, Fore.RED, res.name, res.case_succ, res.case_fail, res.case_skip,
                res.step_succ, res.step_fail, res.assertion_succ, res.assertion_fail,
                durationpy.to_str(res.elapse), Fore.RESET))

    def on_case_end(self, res: CaseResult):
        if res.is_skip:
            print("{}{}case {} 跳过{}".format(self.padding, Fore.YELLOW, res.name, Fore.RESET))
        else:
            print("\n".join([self.padding + i for i in TraceHook.format_case(res, "case")]))

    def on_setup_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TraceHook.format_case(res, "setUp")]))

    def on_teardown_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in TraceHook.format_case(res, "tearDown")]))

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
            lines.extend(["  " + i for i in TraceHook.format_step(step, "beforeCase step")])
        for step in res.pre_steps:
            lines.extend(["  " + i for i in TraceHook.format_step(step, "case preStep")])
        for step in res.steps:
            lines.extend(["  " + i for i in TraceHook.format_step(step, "case step")])
        for step in res.post_steps:
            lines.extend(["  " + i for i in TraceHook.format_step(step, "case postStep")])
        for step in res.after_case_steps:
            lines.extend(["  " + i for i in TraceHook.format_step(step, "afterCase step")])

        return lines

    @staticmethod
    def format_step(step, step_type: str) -> list[str]:
        if step.is_skip:
            return ["{}{} {} 跳过{}".format(Fore.YELLOW, step_type, step.name, Fore.RESET)]

        lines = []
        if step.is_pass:
            lines.append("{}{} {} 通过，断言成功 {}，耗时 {}{}".format(
                Fore.GREEN, step_type, step.name, step.assertion_succ, durationpy.to_str(step.elapse), Fore.RESET,
            ))
        else:
            lines.append("{}{} {} 失败，断言成功 {}，失败 {}，耗时 {}{}".format(
                Fore.RED, step_type, step.name, step.assertion_succ, step.assertion_fail, durationpy.to_str(step.elapse), Fore.RESET,
            ))

        for sub_step in step.sub_steps:
            lines.extend(("req: " + json.dumps(sub_step.req, default=lambda x: str(x), indent=2)).split("\n"))

            if sub_step.is_err:
                lines.extend(("res: " + json.dumps(sub_step.res, indent=2)).split("\n"))
                lines.extend(["  " + i for i in sub_step.err.split("\n")])
                return lines

            # 修改 res 返回值，将预期值标记后拼接在 value 后面
            for expect_result in sub_step.assertions:
                if expect_result.is_pass:
                    TraceHook.append_val_to_key(sub_step.res, expect_result.node, "<GREEN>{}<END>".format(expect_result.expect))
                else:
                    TraceHook.append_val_to_key(sub_step.res, expect_result.node, "<RED>{}<END>".format(expect_result.expect))

            res_lines = ("res: " + json.dumps(sub_step.res, indent=2)).split("\n")
            format_lines = []
            # 解析 res 中 value 的值，重新拼接成带颜色的结果值
            for line in res_lines:
                mr = re.match(r'(\s+".*?": )"(.*)<GREEN>(.*)<END>"(.*)', line)
                if mr:
                    format_lines.append("{}{}{} # {}{}{}".format(
                        mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.GREEN, mr.groups()[2], Fore.RESET,
                    ))
                    continue
                mr = re.match(r'(\s+".*?": )"(.*)<RED>(.*)<END>"(.*)', line)
                if mr:
                    format_lines.append("{}{}{} # {}{}{}".format(
                        mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.RED, mr.groups()[2], Fore.RESET,
                    ))
                    continue
                mr = re.match(r'(\s+)"(.*)<GREEN>(.*)<END>"(.*)', line)
                if mr:
                    format_lines.append("{}{}{} # {}{}{}".format(
                        mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.GREEN, mr.groups()[2], Fore.RESET,
                    ))
                    continue
                mr = re.match(r'(\s+)"(.*)<RED>(.*)<END>"(.*)', line)
                if mr:
                    format_lines.append("{}{}{} # {}{}{}".format(
                        mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], Fore.RED, mr.groups()[2], Fore.RESET,
                    ))
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
