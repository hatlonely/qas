#!/usr/bin/env python3


from datetime import datetime, timezone
from dateutil import parser
from ..result import *


def expect_obj(vals, rules):
    expect_results = []
    if isinstance(rules, dict):
        expect_obj_recursive("", vals, rules, True, expect_results)
    elif isinstance(rules, list):
        expect_obj_recursive("", vals, rules, False, expect_results)
    else:
        pass
    return expect_results


def expect_obj_recursive(root: str, vals, rules, is_dict: bool, expect_results: list):
    if is_dict:
        to_enumerate = rules.items()
    else:
        to_enumerate = enumerate(rules)
    for key, rule in to_enumerate:
        root_dot_key = "{}.{}".format(root, key.lstrip("#")).lstrip(".")
        if isinstance(rule, dict):
            expect_obj_recursive(root_dot_key, vals[key], rule, True, expect_results)
        elif isinstance(rule, list):
            expect_obj_recursive(root_dot_key, vals[key], rule, False, expect_results)
        else:
            if isinstance(key, str) and key.startswith("#"):
                val = vals[key[1:]]
                ok = expect_val(val, rule)
                if not ok:
                    expect_results.append(ExpectResult(is_pass=False, message="NotMatch", node=root_dot_key, val=val, expect=rule))
                else:
                    expect_results.append(ExpectResult(is_pass=True, message="OK", node=root_dot_key, val=val, expect=rule))
            else:
                val = vals[key]
                if val != rule:
                    expect_results.append(ExpectResult(is_pass=False, message="NotEqual", node=root_dot_key, val=val, expect=rule))
                else:
                    expect_results.append(ExpectResult(is_pass=True, message="OK", node=root_dot_key, val=val, expect=rule))


def expect_val(val, rule):
    res = eval(rule)
    if not isinstance(res, bool):
        raise Exception("rule should return result")
    return res


def to_time(val) -> datetime:
    return parser.parse(val)
