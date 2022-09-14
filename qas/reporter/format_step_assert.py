#!/usr/bin/env python3

from ..result import SubStepResult


def format_step_assert(sub_step: SubStepResult, separator="#", pass_open="", pass_close="", fail_open="", fail_close="") -> str:
    lines = []
    for assert_result in sub_step.asserts:
        if assert_result.is_pass:
            lines.append("- {}{}{}".format(pass_open, assert_result.rule, pass_close))
        else:
            lines.append("- {}{}{} {} {}".format(fail_open, assert_result.rule, fail_close, separator, assert_result.message))
    return "\n".join(lines)
