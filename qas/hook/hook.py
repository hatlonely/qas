#!/usr/bin/env python3


from ..result import TestResult, CaseResult, StepResult
from ..i18n import I18n


class Hook:
    def __init__(self, args=None):
        self.i18n = I18n(args).i18n()

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
