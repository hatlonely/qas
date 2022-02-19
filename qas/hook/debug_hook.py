#!/usr/bin/env python3


import json

from .hook import Hook
from ..result import TestResult, CaseResult, StepResult
from ..util import merge


class DebugHook(Hook):
    def __init__(self, args=None):
        super().__init__(args)
        args = merge(args, {
            "padding": "  "
        })
        self.padding_to_add = args["padding"]
        self.padding = ""

    def on_test_start(self, test):
        print("{}{i18n.title.test} {name}".format(self.padding, name=test, i18n=self.i18n))
        self.padding += self.padding_to_add

    def on_test_end(self, res: TestResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{}{i18n.title.test} {res.name}".format(self.padding, res=res, i18n=self.i18n))

    def on_case_start(self, case_info):
        print("{}{i18n.testHeader.case} {name}".format(self.padding, name=case_info["name"], i18n=self.i18n))
        self.padding += self.padding_to_add
        DebugHook.debug_object(self.padding, "CaseInfo", case_info)

    def on_case_end(self, res: CaseResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{}{i18n.testHeader.case} {res.name}".format(self.padding, res=res, i18n=self.i18n))

    def on_set_up_start(self, case_info):
        print("{}{i18n.testHeader.setUp} {name}".format(self.padding, name=case_info["name"], i18n=self.i18n))
        self.padding += self.padding_to_add
        DebugHook.debug_object(self.padding, "SetUpInfo", case_info)

    def on_set_up_end(self, res: CaseResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{}{i18n.testHeader.setUp} {res.name}".format(self.padding, res=res, i18n=self.i18n))

    def on_tear_down_start(self, case_info):
        print("{}{i18n.testHeader.tearDown} {name}".format(self.padding, name=case_info["name"], i18n=self.i18n))
        self.padding += self.padding_to_add
        DebugHook.debug_object(self.padding, "TearDownInfo", case_info)

    def on_tear_down_end(self, res: CaseResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{}{i18n.testHeader.tearDown} {res.name}".format(self.padding, res=res, i18n=self.i18n))

    def on_step_start(self, step_info):
        print("{}{i18n.caseHeader.step} {name}".format(self.padding, name=step_info["name"], i18n=self.i18n))
        self.padding += self.padding_to_add
        DebugHook.debug_object(self.padding, "Step", step_info)

    def on_step_end(self, res: StepResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{}{i18n.caseHeader.step} {res.name}".format(self.padding, res=res, i18n=self.i18n))

    @staticmethod
    def debug_object(padding, title, result):
        print("\n".join([padding + line for line in ("{}: {}".format(title, json.dumps(result, indent=2))).split("\n")]))
