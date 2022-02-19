import json

from qas.reporter import Reporter
from qas.result import TestResult


class SummaryReporter(Reporter):
    def report(self, res: TestResult) -> str:
        return json.dumps({
            "skip": res.case_skip,
            "pass": res.case_pass,
            "fail": res.case_fail,
        }, indent=2)
