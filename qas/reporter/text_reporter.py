#!/usr/bin/env python3


import json
import re

import durationpy
from colorama import Fore
from .reporter import Reporter
from ..result import TestResult, CaseResult
from .format_step_res import format_step_res


class TextReporter(Reporter):
    def __init__(self):
        self.padding = ""

    def report(self, res: TestResult) -> str:
        return "\n".join(self._report(res))

    def _report(self, res: TestResult):
        lines = ["{}进入 {}".format(self.padding, res.directory)]
        self.padding += "  "
        for case in res.setups:
            lines.extend([self.padding + i for i in TextReporter.format_case(case, "setUp")])
        for case in res.cases:
            lines.extend([self.padding + i for i in TextReporter.format_case(case, "case")])
        for case in res.teardowns:
            lines.extend([self.padding + i for i in TextReporter.format_case(case, "tearDown")])
        for sub_test in res.sub_tests:
            lines.extend(self._report(sub_test))
        self.padding = self.padding[:-2]
        if res.is_pass:
            lines.append("{}{}测试 {} 通过，成功 {}，跳过 {}，步骤成功 {}，跳过 {}，断言成功 {}，耗时 {}{}".format(
                self.padding, Fore.GREEN, res.name, res.case_succ, res.case_skip,
                res.step_succ, res.step_skip, res.assertion_succ,
                durationpy.to_str(res.elapse), Fore.RESET,
            ))
        else:
            if res.is_err:
                lines.extend(["  {}  {}".format(self.padding, line) for line in res.err.split("\n")])
            lines.append("{}{}测试 {} 失败，成功 {}，失败 {}，跳过 {}，步骤成功 {}，失败 {}，断言成功 {}，失败 {}，耗时 {}{}".format(
                self.padding, Fore.RED, res.name, res.case_succ, res.case_fail, res.case_skip,
                res.step_succ, res.step_fail, res.assertion_succ, res.assertion_fail,
                durationpy.to_str(res.elapse), Fore.RESET
            ))
        return lines

    @staticmethod
    def format_case(res: CaseResult, case_type: str) -> list[str]:
        lines = []
        if res.is_skip:
            return ["{}case {} 跳过{}".format(Fore.YELLOW, res.name, Fore.RESET)]

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
        for step in res.pre_steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "case preStep")])
        for step in res.steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "case step")])
        for step in res.post_steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "case postStep")])
        for step in res.after_case_steps:
            lines.extend(["  " + i for i in TextReporter.format_step(step, "afterCase step")])

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
            lines.extend(format_step_res(
                sub_step, pass_open=Fore.GREEN, pass_close=Fore.RESET, fail_open=Fore.RED, fail_close=Fore.RESET,
            ).split("\n"))
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
