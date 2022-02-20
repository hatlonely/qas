#!/usr/bin/env python3


import smtplib
import datetime
from email.mime.text import MIMEText
from email.header import Header
from jinja2 import Environment, BaseLoader

from .hook import Hook
from ..util import merge, REQUIRED
from ..result import TestResult


_test_tpl = """
<!DOCTYPE html>
<html lang="zh-cmn-Hans">
<head>
    <title>{{ res.name }} {{ i18n.title.report }}</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
    <div class="row justify-content-md-center mt-5" id={{ name }}><div class="col-md-10">
        {% if res.is_skip %}
        <div class="card border-warning bg-warning">
            <h5 class="card-header text-white bg-transparent border-0">{{ i18n.title.test }} {{ res.name }} {{ i18n.status.skip }}</h5>
        {% elif res.is_pass %}
        <div class="card border-success">
            <h5 class="card-header text-white bg-success">{{ i18n.title.test }} {{ res.name }} {{ i18n.status.succ }}</h5>
        {% else %}
        <div class="card border-danger">
            <h5 class="card-header text-white bg-danger">{{ i18n.title.test }} {{ res.name }} {{ i18n.status.fail }}</h5>
        {% endif %}
    
            {% if not res.is_skip %}
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr class="text-center">
                            <th>{{ i18n.summary.caseTotal }}</th>
                            <th>{{ i18n.summary.casePass }}</th>
                            <th>{{ i18n.summary.caseSkip }}</th>
                            <th>{{ i18n.summary.caseFail }}</th>
                            <th>{{ i18n.summary.stepPass }}</th>
                            <th>{{ i18n.summary.stepSkip }}</th>
                            <th>{{ i18n.summary.stepFail }}</th>
                            <th>{{ i18n.summary.assertionPass }}</th>
                            <th>{{ i18n.summary.assertionFail }}</th>
                            <th>{{ i18n.summary.elapse }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="text-center">
                            {% if res.case_pass %}
                            <td><span class="badge bg-primary rounded-pill">{{ res.case_pass + res.case_skip + res.case_fail }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.case_pass }}</span></td>
                            {% endif %}
    
                            {% if res.case_pass %}
                            <td><span class="badge bg-success rounded-pill">{{ res.case_pass }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.case_pass }}</span></td>
                            {% endif %}
    
                            {% if res.case_skip %}
                            <td><span class="badge bg-warning rounded-pill">{{ res.case_skip }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.case_skip }}</span></td>
                            {% endif %}
    
                            {% if res.case_fail %}
                            <td><span class="badge bg-danger rounded-pill">{{ res.case_fail }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.case_fail }}</span></td>
                            {% endif %}
    
                            {% if res.step_pass %}
                            <td><span class="badge bg-success rounded-pill">{{ res.step_pass }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.step_pass }}</span></td>
                            {% endif %}
    
                            {% if res.step_skip %}
                            <td><span class="badge bg-warning rounded-pill">{{ res.step_skip }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.step_skip }}</span></td>
                            {% endif %}
    
                            {% if res.step_fail %}
                            <td><span class="badge bg-danger rounded-pill">{{ res.step_fail }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.step_fail }}</span></td>
                            {% endif %}
    
                            {% if res.assertion_pass %}
                            <td><span class="badge bg-success rounded-pill">{{ res.assertion_pass }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.assertion_pass }}</span></td>
                            {% endif %}
    
                            {% if res.assertion_fail %}
                            <td><span class="badge bg-danger rounded-pill">{{ res.assertion_fail }}</span></td>
                            {% else %}
                            <td><span class="badge bg-secondary rounded-pill">{{ res.assertion_fail }}</span></td>
                            {% endif %}
    
                            <td>{{ format_timedelta(res.elapse) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            {% endif %}
        </div>
    </div></div>
</body>
"""


class EmailHook(Hook):
    def __init__(self, args):
        super().__init__(args)
        args = merge(args, {
            "endpoint": REQUIRED,
            "username": REQUIRED,
            "password": REQUIRED,
            "receiver": REQUIRED,
            "disableOnPass": False,
        })

        host, port = args["endpoint"].split(":")
        self.host = host
        self.port = port
        self.password = args["password"]
        self.username = args["username"]
        self.receiver = args["receiver"]
        self.disable_on_pass = args["disableOnPass"]

    def on_exit(self, res: TestResult):
        if self.disable_on_pass and res.is_pass:
            return

        body = self.render(res)

        message = MIMEText(body, 'html', 'utf-8')
        message['From'] = Header(self.username, 'utf-8')
        message['To'] = Header(self.receiver, 'utf-8')
        message['Subject'] = Header("{} {}".format(res.name, self.i18n.title.report), 'utf-8')

        smtp = smtplib.SMTP_SSL(self.host, self.port)
        smtp.login(self.username, self.password)
        smtp.sendmail(self.username, self.receiver.split(";"), message.as_string())

    def render(self, res):
        env = Environment(loader=BaseLoader())
        env.globals.update(i18n=self.i18n)
        env.globals.update(format_timedelta=EmailHook.format_timedelta)
        tpl = env.from_string(_test_tpl)
        return tpl.render(res=res)

    @staticmethod
    def format_timedelta(t: datetime.timedelta):
        return "{:.3f}s".format(t.total_seconds())
