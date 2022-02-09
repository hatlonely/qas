#!/usr/bin/env python3


from ..result import TestResult
from .reporter import Reporter


class HtmlReporter(Reporter):
    def report_final_result(self, res: TestResult):
        pass
