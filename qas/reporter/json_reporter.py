#!/usr/bin/env python3


import json

from ..result import TestResult
from .reporter import Reporter


class JsonReporter(Reporter):
    def format(self, res: TestResult):
        print(json.dumps(res, indent=2, default=lambda x: x.to_json()))

    def report_final_result(self, res: TestResult):
        print(json.dumps(res, default=lambda x: x.to_json()))
