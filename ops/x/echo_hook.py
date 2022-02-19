from qas.hook import Hook
from qas.result import TestResult, CaseResult, StepResult


class EchoHook(Hook):
    def on_test_start(self, test):
        print("on test start")

    def on_test_end(self, res: TestResult):
        print("on test end")

    def on_case_start(self, case_info):
        print("on case start")

    def on_case_end(self, res: CaseResult):
        print("on case end")

    def on_step_start(self, step_info):
        print("on step start")

    def on_step_end(self, res: StepResult):
        print("on step end")

    def on_set_up_start(self, case_info):
        print("on set up start")

    def on_set_up_end(self, res: CaseResult):
        print("on set up end")

    def on_tear_down_start(self, case_info):
        print("on tear down start")

    def on_tear_down_end(self, res: CaseResult):
        print("on tear down end")
