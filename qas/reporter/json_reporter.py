#!/usr/bin/env python3


import json

from ..result import TestResult
from ..util import merge
from .reporter import Reporter


class JsonReporter(Reporter):
    def __init__(self, args=None):
        super().__init__(args)
        args = merge(args, {
            "indent": None
        })
        self.indent = args["indent"]

    def report(self, res: TestResult) -> str:
        return json.dumps(res, indent=self.indent, default=lambda x: x.to_json())
