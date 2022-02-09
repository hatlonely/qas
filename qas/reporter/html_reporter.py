#!/usr/bin/env python3


import hashlib

from ..result import TestResult
from .reporter import Reporter

from jinja2 import Environment, BaseLoader
import durationpy

_report_tpl = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ res.name }} 测试报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
</head>

<body>
    {{ body }}
</body>
</html>
"""

_test_tpl = """
<div class="container">
    <div class="row justify-content-md-center">
        <div class="col-lg-10 col-md-12">
            <table class="table table-striped">
                <thead>
                    {% if res.is_pass %}
                    <tr class="table-success"><th colspan="8">{{ res.name }} 测试通过</th></tr>
                    {% else %}
                    <tr class="table-danger"><th colspan="8">{{ res.name }} 测试失败</th></tr>
                    {% endif %}

                    <tr>
                        <th>测试通过</th>
                        <th>测试跳过</th>
                        <th>测试失败</th>
                        <th>步骤通过</th>
                        <th>步骤失败</th>
                        <th>断言成功</th>
                        <th>断言失败</th>
                        <th>耗时</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{{ res.case_succ }}</td>
                        <td>{{ res.case_skip }}</td>
                        <td>{{ res.case_fail }}</td>
                        <td>{{ res.step_succ }}</td>
                        <td>{{ res.step_fail }}</td>
                        <td>{{ res.assertion_succ }}</td>
                        <td>{{ res.assertion_fail }}</td>
                        <td>{{ durationpy.to_str(res.elapse) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="col-lg-10 col-md-12">
            {% set md5sum = "case" + hashlib.md5(res.name.encode()).hexdigest() %}
            <div class="card">
                <div class="card-header">
                    Cases
                </div>
                <ul class="list-group list-group-flush">
                    {% for case in res.cases %}
                    <li class="list-group-item">
                        <h5 class="mb-0">
                            <button
                                class="btn"
                                type="button"
                                data-bs-toggle="collapse"
                                data-bs-target="#{{ md5sum }}{{ loop.index }}"
                                aria-expanded="false"
                                aria-controls="{{ md5sum }}{{ loop.index }}"
                            >
                                {{ case.name }}
                            </button>
                        </h5>
                        <div class="collapse" id="{{ md5sum }}{{ loop.index }}">
                            <div class="card-body">
                                Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute, non cupidatat skateboard dolor brunch. Food truck quinoa nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt aliqua put a bird on it squid single-origin coffee nulla assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft beer labore wes anderson cred nesciunt sapiente ea proident. Ad vegan excepteur butcher vice lomo. Leggings occaecat craft beer farm-to-table, raw denim aesthetic synth nesciunt you probably haven't heard of them accusamus labore sustainable VHS.
                            </div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</div>
"""


class HtmlReporter(Reporter):
    def __init__(self):
        env = Environment(loader=BaseLoader)
        env.globals.update(render=self.render_test)
        env.globals.update(durationpy=durationpy)
        env.globals.update(hashlib=hashlib)
        self.report_tpl = env.from_string(_report_tpl)
        self.test_tpl = env.from_string(_test_tpl)

    def report_final_result(self, res: TestResult):
        print(self.report_tpl.render(res=res, body=self.test_tpl.render(res=res)))

    def render_test(self, res):
        pass

