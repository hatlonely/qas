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
        print("{} 测试开始 {}".format(self.padding, test))
        self.padding += self.padding_to_add

    def on_test_end(self, res: TestResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{} 测试结束 {} {}".format(self.padding, res.directory, json.dumps(res, default=lambda x: x.to_json())))

    def on_case_start(self, case_info):
        print("{} case 开始 {} {}".format(self.padding, case_info["name"], json.dumps(case_info)))
        self.padding += self.padding_to_add

    def on_case_end(self, res: CaseResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{} case 结束 {} {}".format(self.padding, res.name, json.dumps(res, default=lambda x: x.to_json())))

    def on_set_up_start(self, case_info):
        print("{} set_up 开始 {} {}".format(self.padding, case_info["name"], json.dumps(case_info)))
        self.padding += self.padding_to_add

    def on_set_up_end(self, res: CaseResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{} set_up 结束 {} {}".format(self.padding, res.name, json.dumps(res, default=lambda x: x.to_json())))

    def on_tear_down_start(self, case_info):
        print("{} tear_down 开始 {} {}".format(self.padding, case_info["name"], json.dumps(case_info)))
        self.padding += self.padding_to_add

    def on_tear_down_end(self, res: CaseResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{} tear_down 结束 {} {}".format(self.padding, res.name, json.dumps(res, default=lambda x: x.to_json())))

    def on_step_start(self, step_info):
        print("{} step 开始 {} {}".format(self.padding, step_info["name"], json.dumps(step_info)))
        self.padding += self.padding_to_add

    def on_step_end(self, res: StepResult):
        self.padding = self.padding[:-len(self.padding_to_add)]
        print("{} step 结束 {} {}".format(self.padding, res.name, json.dumps(res, default=lambda x: x.to_json())))

