#!/usr/bin/env python3


from ..result import TestResult
from .reporter import Reporter

from jinja2 import Environment, BaseLoader


reporter_tpl = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ res.name }} 测试报告</title>
</head>

<body>
    hello world
</body>
</html>
"""


class HtmlReporter(Reporter):
    def report_final_result(self, res: TestResult):
        template = Environment(loader=BaseLoader).from_string(reporter_tpl)
        print(template.render(res=res))
