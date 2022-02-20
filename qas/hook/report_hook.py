#!/usr/bin/env python3


import json
import durationpy
from colorama import Fore

from .hook import Hook
from ..result import TestResult, CaseResult
from ..reporter import format_step_res
from ..util import merge


class ReportHook(Hook):
    def __init__(self, args=None):
        super().__init__(args)
        args = merge(args, {
            "padding": "  "
        })
        self.padding_to_add = args["padding"]
        self.padding = ""

    def on_test_start(self, directory):
        print("{}{i18n.title.test} {directory}".format(self.padding, directory=directory, i18n=self.i18n))
        self.padding += self.padding_to_add

    def on_test_end(self, res: TestResult):
        self.padding = self.padding[:-len(self.padding_to_add)]

        if res.is_skip:
            print("{}{fore.YELLOW}{i18n.title.test} {res.name} {i18n.status.skip}{fore.RESET}".format(
                self.padding, res=res, i18n=self.i18n, fore=Fore,
            ))
            return

        if res.is_pass:
            print(
                "{}{fore.GREEN}{i18n.title.test} {res.name} {i18n.status.succ}{fore.RESET}，"
                "{i18n.summary.caseTotal}: {total_case}，"
                "{i18n.summary.casePass}: {fore.GREEN}{res.case_pass}{fore.RESET}，"
                "{i18n.summary.caseSkip}: {res.case_skip}，"
                "{i18n.summary.stepPass}: {fore.GREEN}{res.step_pass}{fore.RESET}，"
                "{i18n.summary.stepSkip}: {res.step_skip}，"
                "{i18n.summary.assertionPass}: {fore.GREEN}{res.assertion_pass}{fore.RESET}，"
                "{i18n.summary.elapse}: {elapse}".format(
                    self.padding, total_case=res.case_pass + res.case_skip,
                    elapse=durationpy.to_str(res.elapse), res=res, i18n=self.i18n, fore=Fore,
                ),
            )
        else:
            if res.is_err:
                print('\n'.join([
                    "{}{}{}".format(self.padding_to_add, self.padding, line)
                    for line in "{i18n.testHeader.err} {res.err}".format(res=res, i18n=self.i18n).split("\n")
                ]))
            print(
                "{}{fore.RED}{i18n.title.test} {res.name} {i18n.status.fail}{fore.RESET}，"
                "{i18n.summary.caseTotal}: {total_case}，"
                "{i18n.summary.casePass}: {fore.GREEN}{res.case_pass}{fore.RESET}，"
                "{i18n.summary.caseSkip}: {res.case_skip}，"
                "{i18n.summary.caseFail}: {fore.RED}{res.case_fail}{fore.RESET}，"
                "{i18n.summary.stepPass}: {fore.GREEN}{res.step_pass}{fore.RESET}，"
                "{i18n.summary.stepSkip}: {res.step_skip}，"
                "{i18n.summary.stepFail}: {fore.RED}{res.step_fail}{fore.RESET}，"
                "{i18n.summary.assertionPass}: {fore.GREEN}{res.assertion_pass}{fore.RESET}，"
                "{i18n.summary.assertionFail}: {fore.RED}{res.assertion_fail}{fore.RESET}，"
                "{i18n.summary.elapse}: {elapse}".format(
                    self.padding, total_case=res.case_pass + res.case_skip + res.case_fail,
                    elapse=durationpy.to_str(res.elapse), res=res, i18n=self.i18n, fore=Fore,
                ),
            )

    def on_case_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in self.format_case(res, "case")]))

    def on_set_up_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in self.format_case(res, "setUp")]))

    def on_tear_down_end(self, res: CaseResult):
        print("\n".join([self.padding + i for i in self.format_case(res, "tearDown")]))

    def format_case(self, res: CaseResult, case_type: str) -> list[str]:
        case_type_map = {
            "setUp": self.i18n.testHeader.setUp,
            "tearDown": self.i18n.testHeader.tearDown,
            "case": self.i18n.testHeader.case,
        }

        lines = []
        if res.is_skip:
            return ["{fore.YELLOW}{header} {res.name} {i18n.status.skip}{fore.RESET}".format(
                fore=Fore, res=res, i18n=self.i18n, header=case_type_map[case_type]
            )]

        if res.is_pass:
            lines.append(
                "{fore.GREEN}{header} {res.name} {i18n.status.succ}{fore.RESET}，"
                "{i18n.summary.stepPass}: {fore.GREEN}{res.step_pass}{fore.RESET}，"
                "{i18n.summary.stepSkip}: {res.step_skip}，"
                "{i18n.summary.assertionPass}: {fore.GREEN}{res.assertion_pass}{fore.RESET}，"
                "{i18n.summary.elapse}: {elapse}".format(
                    header=case_type_map[case_type], elapse=durationpy.to_str(res.elapse), fore=Fore, i18n=self.i18n, res=res,
                ),
            )
        else:
            lines.append(
                "{fore.RED}{header} {res.name} {i18n.status.fail}{fore.RESET}，"
                "{i18n.summary.stepPass}: {fore.GREEN}{res.step_pass}{fore.RESET}，"
                "{i18n.summary.stepSkip}: {res.step_skip}，"
                "{i18n.summary.stepFail}: {fore.RED}{res.step_fail}{fore.RESET}，"
                "{i18n.summary.assertionPass}: {fore.GREEN}{res.assertion_pass}{fore.RESET}，"
                "{i18n.summary.assertionFail}: {fore.RED}{res.assertion_fail}{fore.RESET}，"
                "{i18n.summary.elapse}: {elapse}".format(
                    header=case_type_map[case_type], elapse=durationpy.to_str(res.elapse), fore=Fore, i18n=self.i18n, res=res,
                ))

        for step in res.before_case_steps:
            lines.extend([self.padding_to_add + i for i in self.format_step(step, "beforeCaseStep")])
        for step in res.pre_steps:
            lines.extend([self.padding_to_add + i for i in self.format_step(step, "preStep")])
        for step in res.steps:
            lines.extend([self.padding_to_add + i for i in self.format_step(step, "step")])
        for step in res.post_steps:
            lines.extend([self.padding_to_add + i for i in self.format_step(step, "postStep")])
        for step in res.after_case_steps:
            lines.extend([self.padding_to_add + i for i in self.format_step(step, "afterCaseStep")])

        return lines

    def format_step(self, step, step_type: str) -> list[str]:
        step_type_map = {
            "beforeCaseStep": self.i18n.caseHeader.beforeCaseStep,
            "preStep": self.i18n.caseHeader.preStep,
            "step": self.i18n.caseHeader.step,
            "postStep": self.i18n.caseHeader.postStep,
            "afterCaseStep": self.i18n.caseHeader.afterCaseStep,
        }

        if step.is_skip:
            return ["{fore.YELLOW}{header} {step.name} {i18n.status.skip}{fore.RESET}".format(
                fore=Fore, step=step, i18n=self.i18n, header=step_type_map[step_type]
            )]

        lines = []
        if step.is_pass:
            lines.append(
                "{fore.GREEN}{header} {step.name} {i18n.status.succ}{fore.RESET}，"
                "{i18n.summary.assertionPass}: {fore.GREEN}{step.assertion_pass}{fore.RESET}，"
                "{i18n.summary.elapse}: {elapse}".format(
                    fore=Fore, step=step, i18n=self.i18n, header=step_type_map[step_type], elapse=durationpy.to_str(step.elapse),
                ),
            )
        else:
            lines.append(
                "{fore.RED}{header} {step.name} {i18n.status.fail}{fore.RESET}，"
                "{i18n.summary.assertionPass}: {fore.GREEN}{step.assertion_pass}{fore.RESET}，"
                "{i18n.summary.assertionFail}: {fore.RED}{step.assertion_fail}{fore.RESET}，"
                "{i18n.summary.elapse}: {elapse}".format(
                    fore=Fore, step=step, i18n=self.i18n, header=step_type_map[step_type], elapse=durationpy.to_str(step.elapse),
                ),
            )

        for sub_step in step.sub_steps:
            lines.extend((self.i18n.stepHeader.req + ": " + json.dumps(sub_step.req, default=lambda x: str(x), indent=2)).split("\n"))
            if sub_step.is_err:
                lines.extend((self.i18n.stepHeader.res + ": " + json.dumps(sub_step.res, indent=2)).split("\n"))
                lines.extend((self.i18n.stepHeader.err + ": " + sub_step.err).split("\n"))
                return lines
            lines.extend((self.i18n.stepHeader.res + ": " + format_step_res(
                sub_step, pass_open=Fore.GREEN, pass_close=Fore.RESET, fail_open=Fore.RED, fail_close=Fore.RESET,
            )).split("\n"))
        return lines

