#!/usr/bin/env python3


import json

from ..result import TestResult
from .reporter import Reporter


class JsonReporter(Reporter):
    def __init__(self, args=None):
        pass

    def report(self, res: TestResult) -> str:
        return json.dumps(res, default=lambda x: x.to_json())
