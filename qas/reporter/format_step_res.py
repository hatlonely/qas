#!/usr/bin/env python3


import re
import json

from ..result import SubStepResult


def format_step_res(sub_step: SubStepResult, separator="#", pass_open="", pass_close="", fail_open="", fail_close="") -> str:
    # 修改 res 返回值，将预期值标记后拼接在 value 后面
    for expect_result in sub_step.assertions:
        if expect_result.is_pass:
            append_val_to_key(sub_step.res, expect_result.node, "<GREEN>{}<END>".format(expect_result.expect))
        else:
            append_val_to_key(sub_step.res, expect_result.node, "<RED>{}<END>".format(expect_result.expect))

    res_lines = json.dumps(sub_step.res, indent=2).split("\n")
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
