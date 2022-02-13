#!/usr/bin/env python3


import datetime
import hashlib
import json
import re
from jinja2 import Environment, BaseLoader
import markdown

from ..result import TestResult, SubStepResult
from .reporter import Reporter


_report_tpl = """<!DOCTYPE html>
<html lang="zh-cmn-Hans">
<head>
    <title>{{ res.name }} 测试报告</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <style>
        body {
            font-family: 'Oswald', sans-serif !important;
        }
        pre, code {
            font-family: 'Ubuntu Mono', monospace !important;
        }
    </style>
    <script>
        function copyToClipboard(elementId) {
            var aux = document.createElement("textarea");
            aux.value = document.getElementById(elementId).textContent;
            aux.style.height = "0";
            aux.style.overflow = "hidden";
            aux.style.position = "fixed";
            document.body.appendChild(aux);
            aux.select();
            document.execCommand("copy");
            document.body.removeChild(aux);
        }

        function showTestSucc(parentID) {
            $('#' + parentID + ' .test.pass').show()
            $('#' + parentID + ' .test.skip').hide()
            $('#' + parentID + ' .test.fail').hide()
        }

        function showTestSkip(parentID) {
            $('#' + parentID + ' .test.pass').hide()
            $('#' + parentID + ' .test.skip').show()
            $('#' + parentID + ' .test.fail').hide()
        }

        function showTestFail(parentID) {
            $('#' + parentID + ' .test.pass').hide()
            $('#' + parentID + ' .test.skip').hide()
            $('#' + parentID + ' .test.fail').show()
        }

        function showCaseSucc(parentID) {
            $('#' + parentID + ' .case.pass').show()
            $('#' + parentID + ' .case.skip').hide()
            $('#' + parentID + ' .case.fail').hide()
        }

        function showCaseSkip(parentID) {
            $('#' + parentID + ' .case.skip').show()
            $('#' + parentID + ' .case.pass').hide()
            $('#' + parentID + ' .case.fail').hide()
        }

        function showCaseFail(parentID) {
            $('#' + parentID + ' .case.pass').hide()
            $('#' + parentID + ' .case.skip').hide()
            $('#' + parentID + ' .case.fail').show()
        }

        var testToggleStatus = {}
        var caseToggleStatus = {}

        function showAllTest(parentID) {
            if (testToggleStatus[parentID]) {
                $('#' + parentID + ' .test.pass').show()
                $('#' + parentID + ' .test.skip').show()
                $('#' + parentID + ' .test.fail').show()
                testToggleStatus[parentID] = false
            } else {
                $('#' + parentID + ' .test.pass').hide()
                $('#' + parentID + ' .test.skip').hide()
                $('#' + parentID + ' .test.fail').hide()
                testToggleStatus[parentID] = true
            }
        }

        function showAllCase(parentID) {
            if (caseToggleStatus[parentID]) {
                $('#' + parentID + ' .test.pass').show()
                $('#' + parentID + ' .test.skip').show()
                $('#' + parentID + ' .test.fail').show()
                $('#' + parentID + ' .case.pass').show()
                $('#' + parentID + ' .case.skip').show()
                $('#' + parentID + ' .case.fail').show()
                caseToggleStatus[parentID] = false
            } else {
                $('#' + parentID + ' .test.pass').hide()
                $('#' + parentID + ' .test.skip').hide()
                $('#' + parentID + ' .test.fail').hide()
                $('#' + parentID + ' .case.pass').hide()
                $('#' + parentID + ' .case.skip').hide()
                $('#' + parentID + ' .case.fail').hide()
                caseToggleStatus[parentID] = true
            }
        }
    </script>
</head>

<body>
    <div class="container">
        <div class="row justify-content-md-center">
            <div class="col-lg-10 col-md-12">
            {{ render_test(res, "test") }}
            </div>
        </div>
    </div>
</body>

<script>
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    })
</script>
</html>
"""

_test_tpl = """
{% if res.is_pass%}
<div class="col-md-12" id={{ name }}>
{% else %}
<div class="col-md-12" id={{ name }}>
{% endif %}

    {% if res.is_skip %}
    <div class="card my-3 border-warning">
        <div class="card-header text-white bg-warning"><h5>{{ res.name }} 测试跳过</h5></div>
    {% elif res.is_pass %}
    <div class="card my-3 border-success">
        <div class="card-header text-white bg-success"><h5>{{ res.name }} 测试通过</h5></div>
    {% else %}
    <div class="card my-3 border-danger">
        <div class="card-header text-white bg-danger"><h5>{{ res.name }} 测试失败<h5></div>
    {% endif %}

        <div class="card-body">
            <table class="table table-striped">
                <thead>
                    <tr class="text-center">
                        <th>测试总数</th>
                        <th>测试通过</th>
                        <th>测试跳过</th>
                        <th>测试失败</th>
                        <th>步骤通过</th>
                        <th>步骤跳过</th>
                        <th>步骤失败</th>
                        <th>断言成功</th>
                        <th>断言失败</th>
                        <th>耗时</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="text-center">
                        {% if res.case_succ %}
                        <td><span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}')">{{ res.case_succ + res.case_skip + res.case_fail }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.case_succ }}</span></td>
                        {% endif %}

                        {% if res.case_succ %}
                        <td><span class="badge bg-success rounded-pill" onclick="showCaseSucc('{{ name }}')">{{ res.case_succ }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.case_succ }}</span></td>
                        {% endif %}

                        {% if res.case_skip %}
                        <td><span class="badge bg-warning rounded-pill" onclick="showCaseSkip('{{ name }}')">{{ res.case_skip }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.case_skip }}</span></td>
                        {% endif %}

                        {% if res.case_fail %}
                        <td><span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}')">{{ res.case_fail }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.case_fail }}</span></td>
                        {% endif %}

                        {% if res.step_succ %}
                        <td><span class="badge bg-success rounded-pill" onclick="showCasePass('{{ name }}')">{{ res.step_succ }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.step_succ }}</span></td>
                        {% endif %}

                        {% if res.step_skip %}
                        <td><span class="badge bg-warning rounded-pill" onclick="showCaseSkip('{{ name }}')">{{ res.step_skip }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.step_skip }}</span></td>
                        {% endif %}

                        {% if res.step_fail %}
                        <td><span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}')">{{ res.step_fail }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.step_fail }}</span></td>
                        {% endif %}

                        {% if res.assertion_succ %}
                        <td><span class="badge bg-success rounded-pill" onclick="showCaseSucc('{{ name }}')">{{ res.assertion_succ }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.assertion_succ }}</span></td>
                        {% endif %}

                        {% if res.assertion_fail %}
                        <td><span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}')">{{ res.assertion_fail }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.assertion_fail }}</span></td>
                        {% endif %}

                        <td>{{ format_timedelta(res.elapse) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        {# 渲染 Err #}
        {% if res.is_err %}
        <div class="card-header text-white bg-danger">Err</div>
        <div class="card-body"><pre>{{ res.err }}</pre></div>
        {% endif %}

        {# 渲染 Description #}
        {% if res.description %}
        <div class="card-header justify-content-between d-flex">Description</div>
        <div class="card-body">{{ markdown(res.description) }}</div>
        {% endif %}


        {# 渲染 setup #}
        {% if res.setups %}
        <div class="card-header justify-content-between d-flex">
            SetUp
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}-setup')">{{ res.setup_succ + res.setup_fail }}</span>
                {% if res.setup_succ %}
                <span class="badge bg-success rounded-pill" onclick="showCaseSucc('{{ name }}-setup')">{{ res.setup_succ }}</span>
                {% endif %}
                {% if res.setup_fail %}
                <span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}-setup">{{ res.setup_fail }}</span>
                {% endif %}
            </span>
        </div>
        <ul class="list-group list-group-flush" id="{{ name }}-setup">
            {% for case in res.setups %}
            <li class="list-group-item case {{ case.status }}">
                {{ render_case(case, '{}-setup-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# 渲染 case #}
        {% if res.cases %}
        <div class="card-header justify-content-between d-flex {{ "pass" if res.case_fail == 0 else "fail" }}">
            Case
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}-case')">{{ res.curr_case_succ + res.curr_case_skip + res.curr_case_fail }}</span>
                {% if res.curr_case_succ %}
                <span class="badge bg-success rounded-pill" onclick="showCaseSucc('{{ name }}-case')">{{ res.curr_case_succ }}</span>
                {% endif %}
                {% if res.curr_case_skip %}
                <span class="badge bg-warning rounded-pill" onclick="showCaseSkip('{{ name }}-case')">{{ res.curr_case_skip }}</span>
                {% endif %}
                {% if res.curr_case_fail %}
                <span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}-case')">{{ res.curr_case_fail }}</span>
                {% endif %}
            </span>
        </div>
        <ul class="list-group list-group-flush" id="{{ name }}-case">
            {% for case in res.cases %}
            <li class="list-group-item case {{ case.status }}">
                {{ render_case(case, '{}-case-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# 渲染 subtest #}
        {% if res.sub_tests %}
        <div class="card-header justify-content-between d-flex">
            SubTest
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllTest('{{ name }}-subtest')">{{ res.sub_test_succ + res.sub_test_skip + res.sub_test_fail }}</span>
                {% if res.sub_test_succ %}
                <span class="badge bg-success rounded-pill" onclick="showTestSucc('{{ name }}-subtest')">{{ res.sub_test_succ }}</span>
                {% endif %}
                {% if res.sub_test_skip %}
                <span class="badge bg-warning rounded-pill" onclick="showTestSkip('{{ name }}-subtest')">{{ res.sub_test_skip }}</span>
                {% endif %}
                {% if res.sub_test_fail %}
                <span class="badge bg-danger rounded-pill" onclick="showTestFail('{{ name }}-subtest')">{{ res.sub_test_fail }}</span>
                {% endif %}
            </span>
        </div>
        <ul class="list-group list-group-flush" id="{{ name }}-subtest">
            {% for sub_test in res.sub_tests %}
            <li class="list-group-item test {{ sub_test.status }}">
                {{ render_test(sub_test, '{}-subtest-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# 渲染 teardown #}
        {% if res.teardowns %}
        <div class="card-header justify-content-between d-flex">
            TearDown
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}-teardown')">{{ res.teardown_succ + res.teardown_fail }}</span>
                {% if res.teardown_succ %}
                <span class="badge bg-success rounded-pill" onclick="showCaseSucc('{{ name }}-teardown')">{{ res.teardown_succ }}</span>
                {% endif %}
                {% if res.teardown_fail %}
                <span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}-teardown')">{{ res.teardown_fail }}</span>
                {% endif %}
            </span>
        </div>
        <ul class="list-group list-group-flush" id="{{ name }}-teardown">
            {% for case in res.teardowns %}
            <li class="list-group-item case {{ case.status }}">
                {{ render_case(case, '{}-teardown-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
</div>
"""

_case_tpl = """
{% if case.is_skip %}
<a class="card-title btn d-flex justify-content-between align-items-center">
    {{ case.name }}
    <span class="badge bg-warning rounded-pill">skip</span>
</a>
{% elif case.is_pass %}
<a class="card-title btn d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
    {{ case.name }}
    <span>{{ format_timedelta(case.elapse) }}</span>
</a>
{% else %}
<a class="card-title text-white bg-danger btn btn-danger d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
    {{ case.name }}
    <span>{{ format_timedelta(case.elapse) }}</span>
</a>
{% endif %}
<div class="collapse card" id="{{ name }}">
    {% if case.is_pass %}
    <div class="card border-success">
    {% else %}
    <div class="card border-danger">
    {% endif %}
        {# Description #}
        {% if case.description %}
        <div class="card-header">Description</div>
        <div class="card-body">{{ markdown(case.description) }}</div>
        {% endif %}

        {# BeforeCaseStep #}
        {% if case.before_case_steps %}
        <div class="card-header">
            BeforeCaseStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.before_case_steps %}
            <li class="list-group-item">
                {{ render_step(step, '{}-before-case-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {# PreStep #}
        {% if case.pre_steps %}
        <div class="card-header">
            PreStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.pre_steps %}
            <li class="list-group-item">
                {{ render_step(step, '{}-pre-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {# Step #}
        <div class="card-header">
            Step
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.steps %}
            <li class="list-group-item">
                {{ render_step(step, '{}-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        
        {# PostStep #}
        {% if case.pre_steps %}
        <div class="card-header">
            PostStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.post_steps %}
            <li class="list-group-item">
                {{ render_step(step, '{}-post-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# AfterCaseStep #}
        {% if case.after_case_steps %}
        <div class="card-header">
            AfterCaseStep
        </div>
        <ul class="list-group list-group-flush">
            {% for step in case.after_case_steps %}
            <li class="list-group-item">
                {{ render_step(step, '{}-after-case-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
</div>
"""

_step_tpl = """
{% if step.is_skip %}
<a class="card-title btn d-flex justify-content-between align-items-center">
    {{ step.ctx }}
    <span class="badge bg-warning rounded-pill">skip</span>
</a>
{% elif step.is_pass %}
<a class="card-title btn d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
    {{ step.ctx }}.{{ step.name }}
    <span>{{ format_timedelta(step.elapse) }}</span>
</a>
{% else %}
<a class="card-title text-white bg-danger btn btn-danger d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
    {{ step.ctx }}.{{ step.name }}
    <span>{{ format_timedelta(step.elapse) }}</span>
</a>
{% endif %}

<div class="collapse card" id="{{ name }}">
    {% if step.is_pass %}
    <div class="card border-success">
    {% else %}
    <div class="card border-danger">
    {% endif %}
        {# Description #}
        {% if step.description %}
        <div class="card-header">Description</div>
        <div class="card-body">{{ markdown(step.description) }}</div>
        {% endif %}

        {% if not brief_mode %}
        <div class="card-header">
            SubStep
        </div>
        {% endif %}
        <ul class="list-group list-group-flush">
            {% for sub_step in step.sub_steps %}
            <li class="list-group-item">
                {{ render_sub_step(sub_step, '{}-sub-step-{}'.format(name, loop.index0), loop.index0) }}
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
"""

_sub_step_tpl = """
{% if not brief_mode %}
{% if sub_step.is_pass %}
<a class="card-title btn d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
    sub-step {{ index }}
    <span>{{ format_timedelta(sub_step.elapse) }}</span>
</a>
{% else %}
<a class="card-title text-white bg-danger btn btn-danger d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#{{ name }}" role="button" aria-expanded="false" aria-controls="{{ name }}">
    sub-step {{ index }}
    <span>{{ format_timedelta(sub_step.elapse) }}</span>
</a>
{% endif %}
{% endif %}

{% if not brief_mode %}
<div class="collapse card" id="{{ name }}">
{% else %}
<div class="card" id="{{ name }}">
{% endif %}
    {% if sub_step.is_pass %}
    <div class="card border-success">
    {% else %}
    <div class="card border-danger">
    {% endif %}
        <div class="card-header">Req</div>
        <div class="card-body">
            <div class="float-end">
                <button type="button" class="btn btn-sm py-0" onclick="copyToClipboard('{{ name }}-req')"
                    data-bs-toggle="tooltip" data-bs-placement="top" title="复制">
                    <i class="bi-clipboard"></i>
                </button>
            </div>
            <pre id="{{ name }}-req">{{ json.dumps(sub_step.req, indent=2) }}</pre>
        </div>

        {% if sub_step.is_pass or sub_step.is_err %}
        <div class="card-header justify-content-between d-flex">
        {% else %}
        <div class="card-header text-white bg-danger justify-content-between d-flex">
        {% endif %}
            Res
            <span>
                <span class="badge bg-success rounded-pill">{{ sub_step.assertion_succ }}</span>
                {% if sub_step.assertion_fail %}
                <span class="badge bg-danger rounded-pill">{{ sub_step.assertion_fail }}</span>
                {% endif %}
            </span>
        </div>
        <div class="card-body">
            <div class="float-end">
                <button type="button" class="btn btn-sm py-0" onclick="copyToClipboard('{{ name }}-res')"
                    data-bs-toggle="tooltip" data-bs-placement="top" title="复制">
                    <i class="bi-clipboard"></i>
                </button>
            </div>
            <pre id="{{ name }}-res">{{ format_sub_step_res(sub_step) }}</pre>
        </div>

        {% if sub_step.is_err %}
        <div class="card-header text-white bg-danger">Err</div>
        <div class="card-body">
            <pre>{{ sub_step.err }}</pre>
        </div>
        {% endif %}
    </div>
</div>
"""


class HtmlReporter(Reporter):
    def __init__(self):
        env = Environment(loader=BaseLoader)
        env.globals.update(format_timedelta=HtmlReporter.format_timedelta)
        env.globals.update(hashlib=hashlib)
        env.globals.update(json=json)
        env.globals.update(render_test=self.render_test)
        env.globals.update(render_case=self.render_case)
        env.globals.update(render_step=self.render_step)
        env.globals.update(render_sub_step=self.render_sub_step)
        env.globals.update(format_sub_step_res=HtmlReporter.format_sub_step_res)
        env.globals.update(len=len)
        env.globals.update(brief_mode=True)
        env.globals.update(markdown=markdown.markdown)
        self.report_tpl = env.from_string(_report_tpl)
        self.test_tpl = env.from_string(_test_tpl)
        self.case_tpl = env.from_string(_case_tpl)
        self.step_tpl = env.from_string(_step_tpl)
        self.sub_step_tpl = env.from_string(_sub_step_tpl)

    def report(self, res: TestResult) -> str:
        return self.report_tpl.render(res=res)

    def render_test(self, res, name):
        return self.test_tpl.render(res=res, name=name)

    def render_case(self, case, name):
        return self.case_tpl.render(case=case, name=name)

    def render_step(self, step, name):
        return self.step_tpl.render(step=step, name=name)

    def render_sub_step(self, sub_step, name, index):
        return self.sub_step_tpl.render(sub_step=sub_step, name=name, index=index)

    @staticmethod
    def format_sub_step_res(sub_step: SubStepResult) -> str:
        # 修改 res 返回值，将预期值标记后拼接在 value 后面
        for expect_result in sub_step.assertions:
            if expect_result.is_pass:
                HtmlReporter.append_val_to_key(sub_step.res, expect_result.node, "<GREEN>{}<END>".format(expect_result.expect))
            else:
                HtmlReporter.append_val_to_key(sub_step.res, expect_result.node, "<RED>{}<END>".format(expect_result.expect))

        res_lines = json.dumps(sub_step.res, indent=2).split("\n")
        lines = []
        # 解析 res 中 value 的值，重新拼接成带颜色的结果值
        for line in res_lines:
            mr = re.match(r'(\s+".*?": )"(.*)<GREEN>(.*)<END>"(.*)', line)
            if mr:
                lines.append("{}{}{} # <span class='text-success'>{}</span>".format(
                    mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], mr.groups()[2],
                ))
                continue
            mr = re.match(r'(\s+".*?": )"(.*)<RED>(.*)<END>"(.*)', line)
            if mr:
                lines.append("{}{}{} # <span class='text-danger'>{}</span>".format(
                    mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], mr.groups()[2],
                ))
                continue
            mr = re.match(r'(\s+)"(.*)<GREEN>(.*)<END>"(.*)', line)
            if mr:
                lines.append("{}{}{} # <span class='text-success'>{}</span>".format(
                    mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], mr.groups()[2],
                ))
                continue
            mr = re.match(r'(\s+)"(.*)<RED>(.*)<END>"(.*)', line)
            if mr:
                lines.append("{}{}{} # <span class='text-danger'>{}</span>".format(
                    mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], mr.groups()[2],
                ))
                continue
            lines.append(line)
        return '\n'.join(lines)

    @staticmethod
    def append_val_to_key(vals: dict, key, val):
        keys = key.split(".")
        for k in keys[:-1]:
            if isinstance(vals, dict):
                vals = vals[k]
            else:
                vals = vals[int(k)]
        if isinstance(vals, dict):
            vals[keys[-1]] = "{}{}".format(json.dumps(vals[keys[-1]]), val)
        else:
            vals[int(keys[-1])] = "{}{}".format(json.dumps(vals[int(keys[-1])]), val)

    @staticmethod
    def format_timedelta(t: datetime.timedelta):
        return "{:.3f}s".format(t.total_seconds())
