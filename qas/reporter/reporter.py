#!/usr/bin/env python3


from ..result import TestResult, CaseResult, StepResult


class Reporter:
    def report(self, res: TestResult) -> str:
        pass

    def _format(self, res: TestResult):
        self.report_test_start(res.directory)
        for case in res.setups:
            self.report_setup_start(case.name)
            self.report_setup_end(case)
        for case in res.cases:
            self.report_case_start(case.name)
            self.report_case_end(case)
        for case in res.teardowns:
            self.report_teardown_start(case.name)
            self.report_teardown_end(case)
        for sub_test in res.sub_tests:
            self._format(sub_test)
        self.report_test_end(res)

    def format(self, res: TestResult):
        self._format(res)
        self.report_final_result(res)

    def report_final_result(self, res: TestResult):
        pass

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
