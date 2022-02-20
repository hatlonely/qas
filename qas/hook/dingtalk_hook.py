#!/usr/bin/env python3


import hmac
import hashlib
import base64
import urllib.parse
import requests
from datetime import datetime

from .hook import Hook
from ..result import TestResult
from ..util import merge, REQUIRED


class DingTalkHook(Hook):
    def __init__(self, args):
        super().__init__(args)
        args = merge(args, {
            "accessToken": REQUIRED,
            "secret": REQUIRED,
            "actionURL": "",
        })

        self.access_token = args["accessToken"]
        self.secret = args["secret"]
        self.action_url = args["actionURL"]

    def on_exit(self, res: TestResult):
        ts, sign = calculate_sign(self.secret)

        btns = []
        if self.action_url:
            btns.append({
                "title": "查看详情",
                "actionURL": self.action_url,
            })

        res = requests.post(
            url="https://oapi.dingtalk.com/robot/send",
            params={
                "access_token": self.access_token,
                "timestamp": ts,
                "sign": sign,
            },
            headers={
                "Content-Type": "application/json"
            },
            json={
                "msgtype": "actionCard",
                "actionCard": {
                    "title": "{res.name} {i18n.title.report}".format(res=res, i18n=self.i18n),
                    "text": self.render_body(res),
                    "btnOrientation": "0",
                    "btns": btns
                }
            }
        )

        print(res.status_code)
        print(res.text)

    def render_body(self, res: TestResult):
        status = {
            "pass": self.i18n.status.succ,
            "fail": self.i18n.status.fail,
            "skip": self.i18n.status.skip,
        }[res.status]

        return """
#### {res.name} {i18n.title.test} {status}

- **{i18n.summary.casePass}**: {res.case_pass}
- **{i18n.summary.caseFail}**: {res.case_fail}
- **{i18n.summary.caseSkip}**: {res.case_skip}
""".format(res=res, i18n=self.i18n, status=status)


def calculate_sign(secret):
    timestamp = str(round(datetime.now().timestamp() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign
