#!/usr/bin/env python3


from ..result import TestResult, CaseResult, StepResult


class Hook:
    def on_exit(self, res: TestResult):
        pass

    def on_test_start(self, test):
        pass

    def on_test_end(self, res: TestResult):
        pass

    def on_case_start(self, case_info):
        pass

    def on_case_end(self, res: CaseResult):
        pass

    def on_setup_start(self, case_info):
        pass

    def on_setup_end(self, res: CaseResult):
        pass

    def on_teardown_start(self, case_info):
        pass

    def on_teardown_end(self, res: CaseResult):
        pass

    def on_step_start(self, step_info):
        pass

    def on_step_end(self, res: StepResult):
        pass
