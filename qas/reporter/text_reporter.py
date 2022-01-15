#!/usr/bin/env python3


import json
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
            lines.append(Fore.GREEN + "测试通过, 成功 {}".format(len(res.case_results)) + Fore.RESET)
        else:
            lines.append(Fore.RED + "测试失败，成功 {}，失败 {}".format(
                sum(1 for i in res.case_results if i.is_pass),
                sum(1 for i in res.case_results if not i.is_pass),
            ) + Fore.RESET)
        for case_result in res.case_results:
            lines.extend(["  " + i for i in TextReporter.case_summary(case_result)])
        return lines

    @staticmethod
    def case_summary(res: CaseResult) -> list[str]:
        lines = []
        if res.is_pass:
            lines.append(Fore.GREEN + "case {} 通过".format(res.case) + Fore.RESET)
        else:
            lines.append(Fore.RED + "case {} 失败".format(res.case) + Fore.RESET)
        for step_result in res.step_results:
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
        lines.extend(("res: " + json.dumps(res.res, indent=True)).split("\n"))

        for expect_result in res.expect_results:
            lines.append("  {}".format(TextReporter.expect_summary(expect_result)))
        return lines

    @staticmethod
    def expect_summary(res: ExpectResult) -> str:
        if res.is_pass:
            return "node [{}] {}".format(res.node, res.message)
        else:
            return Fore.RED + "node [{}] {}. val: {}, expect: {}".format(res.node, res.message, res.val, res.expect) + Fore.RESET
