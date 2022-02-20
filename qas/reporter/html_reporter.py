#!/usr/bin/env python3


import datetime
import json
from jinja2 import Environment, BaseLoader
import markdown
from types import SimpleNamespace

from ..result import TestResult, SubStepResult
from ..util import merge, REQUIRED
from .reporter import Reporter
from .format_step_res import format_step_res


_report_tpl = """<!DOCTYPE html>
<html lang="zh-cmn-Hans">
<head>
    <title>{{ res.name }} {{ i18n.title.report }}</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    {{ customize.font.style }}
    <style>
        body {
            font-family: {{ customize.font.body }};
        }
        pre, code {
            font-family: {{ customize.font.code }};
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

        function showTestPass(parentID) {
            $('#' + parentID + ' .test.test-skip').hide()
            $('#' + parentID + ' .test.test-fail').hide()
            $('#' + parentID + ' .test.test-pass').show()
        }

        function showTestSkip(parentID) {
            $('#' + parentID + ' .test.test-pass').hide()
            $('#' + parentID + ' .test.test-fail').hide()
            $('#' + parentID + ' .test.test-skip').show()
        }

        function showTestFail(parentID) {
            $('#' + parentID + ' .test.test-pass').hide()
            $('#' + parentID + ' .test.test-skip').hide()
            $('#' + parentID + ' .test.test-fail').show()
        }

        function showCasePass(parentID) {
            $('#' + parentID + ' .test.case-skip').hide()
            $('#' + parentID + ' .test.case-fail').hide()
            $('#' + parentID + ' .test.case-pass').show()
            $('#' + parentID + ' .case.skip').hide()
            $('#' + parentID + ' .case.fail').hide()
            $('#' + parentID + ' .case.pass').show()
        }

        function showCaseSkip(parentID) {
            $('#' + parentID + ' .test.case-pass').hide()
            $('#' + parentID + ' .test.case-fail').hide()
            $('#' + parentID + ' .test.case-skip').show()
            $('#' + parentID + ' .case.pass').hide()
            $('#' + parentID + ' .case.fail').hide()
            $('#' + parentID + ' .case.skip').show()
        }

        function showCaseFail(parentID) {
            $('#' + parentID + ' .test.case-pass').hide()
            $('#' + parentID + ' .test.case-skip').hide()
            $('#' + parentID + ' .test.case-fail').show()
            $('#' + parentID + ' .case.pass').hide()
            $('#' + parentID + ' .case.skip').hide()
            $('#' + parentID + ' .case.fail').show()
        }

        var testToggleStatus = {}
        var caseToggleStatus = {}

        function showAllTest(parentID) {
            if (testToggleStatus[parentID]) {
                $('#' + parentID + ' .test.test-pass').show()
                $('#' + parentID + ' .test.test-skip').show()
                $('#' + parentID + ' .test.test-fail').show()
                testToggleStatus[parentID] = false
            } else {
                $('#' + parentID + ' .test.test-pass').hide()
                $('#' + parentID + ' .test.test-skip').hide()
                $('#' + parentID + ' .test.test-fail').hide()
                testToggleStatus[parentID] = true
            }
        }

        function showAllCase(parentID) {
            if (caseToggleStatus[parentID]) {
                $('#' + parentID + ' .test.test-pass').show()
                $('#' + parentID + ' .test.test-skip').show()
                $('#' + parentID + ' .test.test-fail').show()
                $('#' + parentID + ' .case.pass').show()
                $('#' + parentID + ' .case.skip').show()
                $('#' + parentID + ' .case.fail').show()
                caseToggleStatus[parentID] = false
            } else {
                $('#' + parentID + ' .test.test-pass').hide()
                $('#' + parentID + ' .test.test-skip').hide()
                $('#' + parentID + ' .test.test-fail').hide()
                $('#' + parentID + ' .case.pass').hide()
                $('#' + parentID + ' .case.skip').hide()
                $('#' + parentID + ' .case.fail').hide()
                caseToggleStatus[parentID] = true
            }
        }
    </script>

    {{ customize.extra.head }}
</head>

<body>
    {{ customize.extra.bodyHeader }}
    <div class="container">
        <div class="row justify-content-md-center">
            <div class="col-lg-10 col-md-12">
            {{ render_test(res, "test") }}
            </div>
        </div>
    </div>
    {{ customize.extra.bodyFooter }}
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
<div class="col-md-12" id={{ name }}>
    {% if res.is_skip %}
    <div class="card my-{{ customize.padding.y }} border-warning bg-warning">
        <h5 class="card-header text-white bg-transparent border-0">{{ i18n.title.test }} {{ res.name }} {{ i18n.status.skip }}</h5>
    {% elif res.is_pass %}
    <div class="card my-{{ customize.padding.y }} border-success">
        <h5 class="card-header text-white bg-success">{{ i18n.title.test }} {{ res.name }} {{ i18n.status.succ }}</h5>
    {% else %}
    <div class="card my-{{ customize.padding.y }} border-danger">
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
                        <td><span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}')">{{ res.case_pass + res.case_skip + res.case_fail }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.case_pass }}</span></td>
                        {% endif %}

                        {% if res.case_pass %}
                        <td><span class="badge bg-success rounded-pill" onclick="showCasePass('{{ name }}')">{{ res.case_pass }}</span></td>
                        {% else %}
                        <td><span class="badge bg-secondary rounded-pill">{{ res.case_pass }}</span></td>
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
        
        {# 渲染 Err #}
        {% if res.is_err %}
        <div class="card-header text-white bg-danger"><span class="fw-bolder">{{ i18n.testHeader.err }}</span></div>
        <div class="card-body"><pre>{{ res.err }}</pre></div>
        {% endif %}

        {# 渲染 Description #}
        {% if res.description %}
        <div class="card-header justify-content-between d-flex"><span class="fw-bolder">{{ i18n.testHeader.description }}</span></div>
        <div class="card-body">{{ markdown(res.description) }}</div>
        {% endif %}


        {# 渲染 set_up #}
        {% if res.set_ups %}
        <div class="card-header justify-content-between d-flex">
            <span class="fw-bolder">{{ i18n.testHeader.setUp }}</span>
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}-set-up')">{{ res.set_up_pass + res.set_up_fail }}</span>
                {% if res.set_up_pass %}
                <span class="badge bg-success rounded-pill" onclick="showCasePass('{{ name }}-set-up')">{{ res.set_up_pass }}</span>
                {% endif %}
                {% if res.set_up_fail %}
                <span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}-set-up">{{ res.set_up_fail }}</span>
                {% endif %}
            </span>
        </div>
        <ul class="list-group list-group-flush" id="{{ name }}-set-up">
            {% for case in res.set_ups %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }} case {{ case.status }}">
                {{ render_case(case, '{}-set-up-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# 渲染 case #}
        {% if res.cases %}
        <div class="card-header justify-content-between d-flex {{ "pass" if res.case_fail == 0 else "fail" }}">
            <span class="fw-bolder">{{ i18n.testHeader.case }}</span>
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}-case')">{{ res.curr_case_pass + res.curr_case_skip + res.curr_case_fail }}</span>
                {% if res.curr_case_pass %}
                <span class="badge bg-success rounded-pill" onclick="showCasePass('{{ name }}-case')">{{ res.curr_case_pass }}</span>
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
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }} case {{ case.status }}">
                {{ render_case(case, '{}-case-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# 渲染 subtest #}
        {% if res.sub_tests %}
        <div class="card-header justify-content-between d-flex">
            <span class="fw-bolder">{{ i18n.testHeader.subTest }}</span>
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllTest('{{ name }}-subtest')">{{ res.sub_test_pass + res.sub_test_skip + res.sub_test_fail }}</span>
                {% if res.sub_test_pass %}
                <span class="badge bg-success rounded-pill" onclick="showTestPass('{{ name }}-subtest')">{{ res.sub_test_pass }}</span>
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
            <li class="
                list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }} test
                test-{{ sub_test.status }}
                {% if sub_test.case_pass %}case-pass{% endif %}
                {% if sub_test.case_skip %}case-skip{% endif %}
                {% if sub_test.case_fail %}case-fail{% endif %}
            ">
                {{ render_test(sub_test, '{}-subtest-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# 渲染 tear_down #}
        {% if res.tear_downs %}
        <div class="card-header justify-content-between d-flex">
            <span class="fw-bolder">{{ i18n.testHeader.tearDown }}</span>
            <span>
                <span class="badge bg-primary rounded-pill" onclick="showAllCase('{{ name }}-tear-down')">{{ res.tear_down_pass + res.tear_down_fail }}</span>
                {% if res.tear_down_pass %}
                <span class="badge bg-success rounded-pill" onclick="showCasePass('{{ name }}-tear-down')">{{ res.tear_down_pass }}</span>
                {% endif %}
                {% if res.tear_down_fail %}
                <span class="badge bg-danger rounded-pill" onclick="showCaseFail('{{ name }}-tear-down')">{{ res.tear_down_fail }}</span>
                {% endif %}
            </span>
        </div>
        <ul class="list-group list-group-flush" id="{{ name }}-tear-down">
            {% for case in res.tear_downs %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }} case {{ case.status }}">
                {{ render_case(case, '{}-tear-down-{}'.format(name, loop.index0)) }}
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
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.description }}</span></div>
        <div class="card-body">{{ markdown(case.description) }}</div>
        {% endif %}
        
        {% if case.command %}
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.command }}</span></div>
        <div class="card-body">
            <div class="float-end">
                <button type="button" class="btn btn-sm py-0" onclick="copyToClipboard('{{ name }}-command')"
                    data-bs-toggle="tooltip" data-bs-placement="top" title="{{ i18n.toolTips.copy }}">
                    <i class="bi-clipboard"></i>
                </button>
            </div>
            <span id="{{ name }}-command">{{ case.command }}</span>
        </div>        
        {% endif %}

        {# BeforeCaseStep #}
        {% if case.before_case_steps %}
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.beforeCaseStep }}</span></div>
        <ul class="list-group list-group-flush">
            {% for step in case.before_case_steps %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }}">
                {{ render_step(step, '{}-before-case-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {# PreStep #}
        {% if case.pre_steps %}
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.preStep }}</span></div>
        <ul class="list-group list-group-flush">
            {% for step in case.pre_steps %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }}">
                {{ render_step(step, '{}-pre-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {# Step #}
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.step }}</span></div>
        <ul class="list-group list-group-flush">
            {% for step in case.steps %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }}">
                {{ render_step(step, '{}-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        
        {# PostStep #}
        {% if case.pre_steps %}
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.postStep }}</span></div>
        <ul class="list-group list-group-flush">
            {% for step in case.post_steps %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }}">
                {{ render_step(step, '{}-post-step-{}'.format(name, loop.index0)) }}
            </li>
            {% endfor %}
        </ul>
        {% endif %}

        {# AfterCaseStep #}
        {% if case.after_case_steps %}
        <div class="card-header"><span class="fw-bolder">{{ i18n.caseHeader.afterCaseStep }}</span></div>
        <ul class="list-group list-group-flush">
            {% for step in case.after_case_steps %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }}">
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
        <div class="card-header"><span class="fw-bolder">{{ i18n.stepHeader.description }}</span></div>
        <div class="card-body">{{ markdown(step.description) }}</div>
        {% endif %}

        {% if not brief_mode %}
        <div class="card-header"><span class="fw-bolder">{{ i18n.stepHeader.subStep }}</span></div>
        {% endif %}
        <ul class="list-group list-group-flush">
            {% for sub_step in step.sub_steps %}
            <li class="list-group-item px-{{ customize.padding.x }} py-{{ customize.padding.y }}">
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
        <div class="card-header"><span class="fw-bolder">{{ i18n.stepHeader.req }}</span></div>
        <div class="card-body">
            <div class="float-end">
                <button type="button" class="btn btn-sm py-0" onclick="copyToClipboard('{{ name }}-req')"
                    data-bs-toggle="tooltip" data-bs-placement="top" title="{{ i18n.toolTips.copy }}">
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
            <span class="fw-bolder">{{ i18n.stepHeader.res }}</span>
            <span>
                <span class="badge bg-success rounded-pill">{{ sub_step.assertion_pass }}</span>
                {% if sub_step.assertion_fail %}
                <span class="badge bg-danger rounded-pill">{{ sub_step.assertion_fail }}</span>
                {% endif %}
            </span>
        </div>
        <div class="card-body">
            <div class="float-end">
                <button type="button" class="btn btn-sm py-0" onclick="copyToClipboard('{{ name }}-res')"
                    data-bs-toggle="tooltip" data-bs-placement="top" title="{{ i18n.toolTips.copy }}">
                    <i class="bi-clipboard"></i>
                </button>
            </div>
            <pre id="{{ name }}-res">{{ format_sub_step_res(sub_step) }}</pre>
        </div>

        {% if sub_step.is_err %}
        <div class="card-header text-white bg-danger"><span class="fw-bolder">{{ i18n.stepHeader.err }}</span></div>
        <div class="card-body">
            <pre>{{ sub_step.err }}</pre>
        </div>
        {% endif %}
    </div>
</div>
"""


class HtmlReporter(Reporter):
    def __init__(self, args=None):
        super().__init__(args)
        args = merge(args, {
            "stepSeparator": "#",
            "font": {
                "style": """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Roboto+Condensed:wght@400;700&display=swap" rel="stylesheet">
""",
                "body": "'Roboto Condensed', sans-serif !important",
                "code": "'JetBrains Mono', monospace !important",
            },
            "extra": {
                "head": "",
                "bodyHeader": "",
                "bodyFooter": "",
            },
            "padding": {
                "x": 2,
                "y": 2,
            }
        })
        self.step_separator = args["stepSeparator"]
        self.customize = json.loads(json.dumps(args), object_hook=lambda x: SimpleNamespace(**x))

        env = Environment(loader=BaseLoader())
        env.globals.update(format_timedelta=HtmlReporter.format_timedelta)
        env.globals.update(json=json)
        env.globals.update(render_test=self.render_test)
        env.globals.update(render_case=self.render_case)
        env.globals.update(render_step=self.render_step)
        env.globals.update(render_sub_step=self.render_sub_step)
        env.globals.update(format_sub_step_res=self.format_sub_step_res)
        env.globals.update(brief_mode=True)
        env.globals.update(markdown=markdown.markdown)
        env.globals.update(i18n=self.i18n)
        env.globals.update(customize=self.customize)
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

    def format_sub_step_res(self, sub_step: SubStepResult) -> str:
        return format_step_res(
            sub_step, separator=self.step_separator,
            pass_open="<span class='text-success'>", pass_close="</span>",
            fail_open="<span class='text-danger'>", fail_close="</span>",
        )

    @staticmethod
    def format_timedelta(t: datetime.timedelta):
        return "{:.3f}s".format(t.total_seconds())
