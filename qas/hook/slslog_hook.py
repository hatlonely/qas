#!/usr/bin/env python3


from datetime import datetime
from aliyun.log import LogClient, PutLogsRequest, LogItem, GetLogsRequest

from .hook import Hook
from ..result import TestResult, CaseResult, StepResult
from ..util import merge, REQUIRED


class SLSLogHook(Hook):
    def __init__(self, args):
        super().__init__(args)

        args = merge(args, {
            "Endpoint": REQUIRED,
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "Project": REQUIRED,
            "Logstore": REQUIRED,
            "Topic": None,
            "Source": None,
            "HashKey": None,
            "LogTags": {}
        })

        self.client = LogClient(
            args["Endpoint"],
            args["AccessKeyId"],
            args["AccessKeySecret"],
        )
        self.project = args["Project"]
        self.logstore = args["Logstore"]
        self.topic = args["Topic"]
        self.source = args["Source"]
        self.hash_key = args["HashKey"]
        self.log_tags = args["LogTags"]

    def on_exit(self, res: TestResult):
        self.log(res.name, "test", res.status, res.elapse, {
            "casePass": res.case_pass,
            "caseFail": res.case_fail,
            "caseSkip": res.case_skip,
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_test_end(self, res: TestResult):
        self.log(res.name, "subTest", res.status, res.elapse, {
            "casePass": res.case_pass,
            "caseFail": res.case_fail,
            "caseSkip": res.case_skip,
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_set_up_end(self, res: CaseResult):
        self.log(res.name, "setUp", res.status, res.elapse, {
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_case_end(self, res: CaseResult):
        self.log(res.name, "case", res.status, res.elapse, {
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_tear_down_end(self, res: CaseResult):
        self.log(res.name, "tearDown", res.status, res.elapse, {
            "stepPass": res.step_pass,
            "stepFail": res.step_fail,
            "stepSkip": res.step_skip,
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def on_step_end(self, res: StepResult):
        if res.is_skip:
            status = "skip"
        elif res.is_pass:
            status = "pass"
        else:
            status = "fail"
        self.log(res.name, "step", status, res.elapse, {
            "assertionPass": res.assertion_pass,
            "assertionFail": res.assertion_fail,
        })

    def log(self, name, type_, status, elapse, detail):
        self.client.put_logs(PutLogsRequest(
            project=self.project,
            logstore=self.logstore,
            topic=self.topic,
            source=self.source,
            hashKey=self.hash_key,
            logtags=self.log_tags.items(),
            logitems=[
                LogItem(
                    timestamp=int(datetime.now().timestamp()),
                    contents=[
                        ("type", type_),
                        ("status", status),
                        ("elapseMs", str(int(elapse.total_seconds() * 1000))),
                        *[(k, str(v)) for k, v in detail.items()],
                    ],
                )
            ]
        ))
