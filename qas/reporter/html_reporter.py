#!/usr/bin/env python3


import hashlib
import json

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
    <div class="container">
        <div class="row justify-content-md-center">
            <div class="col-lg-10 col-md-12">
            {% print(render_test(res, "test")) %}
            </div>
        </div>
    </div>
</body>
</html>
"""

_test_tpl = """
<div class="col-md-12">
    <div class="card mt-3">
        {% if res.is_pass %}
        <div class="card-header text-white bg-success">{{ res.name }}测试通过</div>
        {% else %}
        <div class="card-header text-white bg-danger">{{ res.name }}测试失败</div>
        {% endif %}
        
        <div class="card-body">
            <table class="table table-striped">
                <thead>
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
    </div>
</div>

{# 渲染 setup #}
{% if res.setups %}
<div class="col-md-12">
    <div class="card mt-3">
        <div class="card-header">
            SetUp
        </div>
        <ul class="list-group list-group-flush">
            {% for case in res.setups %}
            <li class="list-group-item">
                {% print(render_case(case, '{}-setup-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
{% endif %}

{# 渲染 case #}
{% if res.cases %}
<div class="col-md-12">
    <div class="card mt-3">
        <div class="card-header">
            Case
        </div>
        <ul class="list-group list-group-flush">
            {% for case in res.cases %}
            <li class="list-group-item">
                {% print(render_case(case, '{}-case-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
{% endif %}

{# 渲染 teardown #}
{% if res.teardowns %}
<div class="col-md-12">
    <div class="card mt-3">
        <div class="card-header">
            TearDown
        </div>
        <ul class="list-group list-group-flush">
            {% for case in res.teardowns %}
            <li class="list-group-item">
                {% print(render_case(case, '{}-teardown-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
{% endif %}

{# 渲染 subtest #}
{% if res.sub_tests %}
<div class="col-md-12">
    <div class="card mt-3">
        <div class="card-header">
            SubTest
        </div>
        <ul class="list-group list-group-flush">
            {% for sub_test in res.sub_tests %}
            <li class="list-group-item">
                {% print(render_test(sub_test, '{}-subtest-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
{% endif %}
"""

_case_tpl = """
<h5 class="card-title">
    <a class="btn" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
        {{ case.name }}
    </a>
</h5>
<div class="collapse card" id="{{ name }}">
    <div class="card">
        {# BeforeCaseStep #}
        <div class="card-header">
            BeforeCaseStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.before_case_steps %}
            <li class="list-group-item">
                {% print(render_step(step, '{}-step-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
        
        {# PreStep #}
        <div class="card-header">
            PreStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.pre_steps %}
            <li class="list-group-item">
                {% print(render_step(step, '{}-step-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
        
        {# Step #}
        <div class="card-header">
            Step
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.steps %}
            <li class="list-group-item">
                {% print(render_step(step, '{}-step-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
        
        {# AfterCaseStep #}
        <div class="card-header">
            AfterCaseStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.after_case_steps %}
            <li class="list-group-item">
                {% print(render_step(step, '{}-step-{}'.format(name, loop.index0))) %}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
"""

_step_tpl = """
<h5 class="card-title">
    <a class="btn" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
        {{ step.name }}
    </a>
</h5>

<div class="collapse card" id="{{ name }}">
    <div class="card">
        <div class="card-header">
            SubStep
        </div>
        <ul class="list-group list-group-flush">
            {% for sub_step in step.sub_steps %}
            <li class="list-group-item">
                {% print(render_sub_step(sub_step, '{}-sub-step-{}'.format(name, loop.index0), loop.index0)) %}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
"""

_sub_step_tpl = """
<h5 class="card-title">
    <a class="btn" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
        sub-step {{ index }}
    </a>
</h5>

<div class="collapse card" id="{{ name }}">
    <div class="card border-success">
        <div class="card-header">
            Req
        </div>
        <div class="card-body">
            <pre>{% print(json.dumps(sub_step.req, indent=2)) %}</pre>
        </div>
        <div class="card-header">
            Res
        </div>
        <div class="card-body">
            <pre>{% print(json.dumps(sub_step.res, indent=2)) %}</pre>
        </div>
    </div>
</div>
"""


class HtmlReporter(Reporter):
    def __init__(self):
        env = Environment(loader=BaseLoader)
        env.globals.update(durationpy=durationpy)
        env.globals.update(hashlib=hashlib)
        env.globals.update(json=json)
        env.globals.update(render_test=self.render_test)
        env.globals.update(render_case=self.render_case)
        env.globals.update(render_step=self.render_step)
        env.globals.update(render_sub_step=self.render_sub_step)
        self.report_tpl = env.from_string(_report_tpl)
        self.test_tpl = env.from_string(_test_tpl)
        self.case_tpl = env.from_string(_case_tpl)
        self.step_tpl = env.from_string(_step_tpl)
        self.sub_step_tpl = env.from_string(_sub_step_tpl)

    def report_final_result(self, res: TestResult):
        print(self.report_tpl.render(res=res))

    def render_test(self, res, name):
        return self.test_tpl.render(res=res, name=name)

    def render_case(self, case, name):
        return self.case_tpl.render(case=case, name=name)

    def render_step(self, step, name):
        return self.step_tpl.render(step=step, name=name)

    def render_sub_step(self, sub_step, name, index):
        return self.sub_step_tpl.render(sub_step=sub_step, name=name, index=index)
