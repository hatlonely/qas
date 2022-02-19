#!/usr/bin/env python3
import copy
import re
import json

from ..result import SubStepResult


def format_step_res(sub_step: SubStepResult, separator="#", pass_open="", pass_close="", fail_open="", fail_close="") -> str:
    if len(sub_step.assertions) == 1 and sub_step.assertions[0].node == "":
        if sub_step.assertions[0].is_pass:
            return "{} {} {}{}{}".format(
                json.dumps(sub_step.res, indent=2), separator, pass_open, sub_step.assertions[0].expect, pass_close
            )
        else:
            return "{} {} {}{}{}".format(
                json.dumps(sub_step.res, indent=2), separator, fail_open, sub_step.assertions[0].expect, fail_close
            )

    # 修改 res 返回值，将预期值标记后拼接在 value 后面
    res = copy.deepcopy(sub_step.res)
    for expect_result in sub_step.assertions:
        if expect_result.is_pass:
            append_val_to_key(res, expect_result.node, "<GREEN>{}<END>".format(expect_result.expect))
        else:
            append_val_to_key(res, expect_result.node, "<RED>{}<END>".format(expect_result.expect))

    res_lines = json.dumps(res, indent=2).split("\n")
    lines = []
    # 解析 res 中 value 的值，重新拼接成带颜色的结果值
    for line in res_lines:
        mr = re.match(r'(\s+".*?": )"(.*)<GREEN>(.*)<END>"(.*)', line)
        if mr:
            lines.append("{}{}{} {} {}{}{}".format(
                mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], separator, pass_open, mr.groups()[2], pass_close
            ))
            continue
        mr = re.match(r'(\s+".*?": )"(.*)<RED>(.*)<END>"(.*)', line)
        if mr:
            lines.append("{}{}{} {} {}{}{}".format(
                mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], separator, fail_open, mr.groups()[2], fail_close
            ))
            continue
        mr = re.match(r'(\s+)"(.*)<GREEN>(.*)<END>"(.*)', line)
        if mr:
            lines.append("{}{}{} {} {}{}{}".format(
                mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], separator, pass_open, mr.groups()[2], pass_close
            ))
            continue
        mr = re.match(r'(\s+)"(.*)<RED>(.*)<END>"(.*)', line)
        if mr:
            lines.append("{}{}{} {} {}{}{}".format(
                mr.groups()[0], json.loads('"{}"'.format(mr.groups()[1])), mr.groups()[3], separator, fail_open, mr.groups()[2], fail_close
            ))
            continue
        lines.append(line)
    return '\n'.join(lines)


def append_val_to_key(vals, node, val):
    keys = node.split(".")
    for k in keys[:-1]:
        if isinstance(vals, dict):
            vals = vals[k]
        else:
            vals = vals[int(k)]

    key = keys[-1]
    if isinstance(vals, dict):
        if key in vals:
            vals[key] = "{}{}".format(json.dumps(vals[key]), val)
        else:
            vals[key] = "{}{}".format(json.dumps(None), val)
    else:
        if int(key) < len(vals):
            vals[int(key)] = "{}{}".format(json.dumps(vals[int(key)]), val)
        else:
            vals.append("{}{}".format(json.dumps(None), val))
