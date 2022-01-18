#!/usr/bin/env python3


from datetime import datetime, timezone
from dateutil import parser
from ..result import *


def expect(vals, rules, case=None, var=None):
    expect_results = []
    if isinstance(rules, dict):
        _expect_recursive("", vals, rules, True, expect_results, case=case, var=var)
    elif isinstance(rules, list):
        _expect_recursive("", vals, rules, False, expect_results, case=case, var=var)
    else:
        pass
    return expect_results


def _expect_recursive(root: str, vals, rules, is_dict: bool, expect_results: list, case=None, var=None):
    if is_dict:
        to_enumerate = rules.items()
    else:
        to_enumerate = enumerate(rules)
    for key, rule in to_enumerate:
        root_dot_key = "{}.{}".format(root, key.lstrip("#")).lstrip(".")
        if isinstance(rule, dict):
            _expect_recursive(root_dot_key, vals[key], rule, True, expect_results, case=case, var=var)
        elif isinstance(rule, list):
            _expect_recursive(root_dot_key, vals[key], rule, False, expect_results, case=case, var=var)
        else:
            if isinstance(key, str) and key.startswith("#"):
                val = vals[key[1:]]
                ok = expect_val(val, rule, case=case, var=var)
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


def expect_val(val, rule, case=None, var=None):
    res = eval(rule)
    if not isinstance(res, bool):
        return res == val
    return res


def to_time(val) -> datetime:
    return parser.parse(val)
