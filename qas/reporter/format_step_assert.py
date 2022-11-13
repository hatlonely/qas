#!/usr/bin/env python3

import html
from ..result import SubStepResult


def format_step_assert(sub_step: SubStepResult, separator="#", pass_open="", pass_close="", fail_open="", fail_close="", html_escape=False) -> str:
    lines = []
    for assert_result in sub_step.asserts:
        if assert_result.is_pass:
            lines.append("- {}{}{}".format(pass_open, assert_result.rule, pass_close))
        else:
            message = assert_result.message
            if html_escape:
                message = html.escape(assert_result.message)
            lines.append("- {}{}{} {} {}".format(fail_open, assert_result.rule, fail_close, separator, message))
    return "\n".join(lines)
