#!/usr/bin/env python3

from ..result import TestResult, CaseResult, StepResult, ExpectResult


class Reporter:
    def report_test_start(self, info):
        pass

    def report_test_end(self, res: TestResult):
        pass

    def report_case_start(self, case):
        pass

    def report_case_end(self, res: CaseResult):
        pass

    def report_skip_case(self, name):
        pass

    def report_setup_start(self, case):
        pass

    def report_setup_end(self, res: CaseResult):
        pass

    def report_teardown_start(self, result):
        pass

    def report_teardown_end(self, res: CaseResult):
        pass

    def report_step_start(self, step):
        pass

    def report_step_end(self, res: StepResult):
        pass

    def report_skip_step(self, name):
        pass
