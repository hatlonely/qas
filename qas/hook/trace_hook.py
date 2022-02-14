#!/usr/bin/env python3


import json
import durationpy
from colorama import Fore

from .hook import Hook
from ..result import TestResult, CaseResult
from ..reporter import format_step_res


class TraceHook(Hook):
    def __init__(self, args=None):
        self.padding = ""

    def on_test_start(self, directory):
        print("{}进入 {}".format(self.padding, directory))
        self.padding += "  "

    def on_test_end(self, res: TestResult):
        self.padding = self.padding[:-2]
        if res.is_pass:
            print(
                "{}{}测试 {res.name} 通过，成功 {res.case_pass}，跳过 {res.case_skip}，"
                "步骤成功 {res.step_pass}，跳过 {res.step_skip}，断言成功 {res.assertion_pass}，"
                "耗时 {}{}".format(
                    self.padding, Fore.GREEN, durationpy.to_str(res.elapse), Fore.RESET, res=res,
                ))
        else:
            if res.is_err:
                print('\n'.join([
                    "  {}  {}".format(self.padding, line)
                    for line in res.err.split("\n")
                ]))
            print(
                "{}{}测试 {res.name} 失败，成功 {res.case_pass}，失败 {res.case_fail}，跳过 {res.case_pass}，"
                "步骤成功 {res.step_pass}，跳过 {res.step_skip}，失败 {res.step_fail}，"
                "断言成功 {res.assertion_pass}，失败 {res.assertion_fail}，耗时 {}{}".format(
                    self.padding, Fore.RED, durationpy.to_str(res.elapse), Fore.RESET, res=res,
                ))

    def on_case_end(self, res: CaseResult):
        if res.is_skip:
            print("{}case {res.name} 跳过{}".format(Fore.YELLOW, Fore.RESET, res=res))
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
            lines.append("{}{case_type} {res.name} 通过，步骤成功 {res.step_pass}，断言成功 {res.assertion_pass}，耗时 {}{}".format(
                Fore.GREEN, durationpy.to_str(res.elapse), Fore.RESET, case_type=case_type, res=res,
            ))
        else:
            lines.append(
                "{}{case_type} {res.name} 失败，步骤成功 {res.step_pass}，失败 {res.step_fail}，"
                "断言成功 {res.assertion_pass}，失败 {res.assertion_fail}，耗时 {}{}".format(
                    Fore.RED, durationpy.to_str(res.elapse), Fore.RESET, case_type=case_type, res=res,
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
            return ["{}{step_type} {step.name} 跳过{}".format(Fore.YELLOW, Fore.RESET, step_type=step_type, step=step)]

        lines = []
        if step.is_pass:
            lines.append("{}{step_type} {step.name} 通过，断言成功 {step.assertion_pass}，耗时 {}{}".format(
                Fore.GREEN, durationpy.to_str(step.elapse), Fore.RESET, step_type=step_type, step=step
            ))
        else:
            lines.append("{}{step_type} {step.name} 失败，断言成功 {step.assertion_pass}，失败 {step.assertion_fail}，耗时 {}{}".format(
                Fore.RED, durationpy.to_str(step.elapse), Fore.RESET, step_type=step_type, step=step
            ))

        for sub_step in step.sub_steps:
            lines.extend(("req: " + json.dumps(sub_step.req, default=lambda x: str(x), indent=2)).split("\n"))

            if sub_step.is_err:
                lines.extend(("res: " + json.dumps(sub_step.res, indent=2)).split("\n"))
                lines.extend(["  " + i for i in sub_step.err.split("\n")])
                return lines
            res_lines = format_step_res(
                sub_step, pass_open=Fore.GREEN, pass_close=Fore.RESET, fail_open=Fore.RED, fail_close=Fore.RESET,
            ).split("\n")
            if res_lines:
                res_lines[0] = "res: {}".format(res_lines[0])
            lines.extend(res_lines)
        return lines
