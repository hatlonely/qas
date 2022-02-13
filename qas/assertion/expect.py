#!/usr/bin/env python3


from ..result import ExpectResult
from ..util.include import *


def expect(vals, rules, case=None, step=None, var=None, x=None):
    results = []
    _expect_recursive("", results, vals, rules, case=case, step=step, var=var, x=x)
    return results


def _expect_recursive(root: str, results: list[ExpectResult], vals, rules, case=None, step=None, var=None, x=None):
    if isinstance(rules, dict):
        for key, rule in rules.items():
            root_dot_key = "{}.{}".format(root, key.lstrip("#").lstrip("%")).lstrip(".")
            if key.startswith("%"):
                if key[1:] not in vals:
                    results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
                else:
                    results.append(run_expect(root_dot_key, rule, "exec", val=vals[key[1:]], case=case, step=step, var=var, x=x))
            elif key.startswith("#"):
                if key[1:] not in vals:
                    results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
                else:
                    results.append(run_expect(root_dot_key, rule, "eval", val=vals[key[1:]], case=case, step=step, var=var, x=x))
            elif key not in vals:
                results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
            elif isinstance(rule, dict) or isinstance(rule, list):
                if not isinstance(vals[key], type(rule)):
                    results.append(ExpectResult(is_pass=False, message="TypeDiff", node=root_dot_key, val=vals[key], expect=rule))
                else:
                    _expect_recursive(root_dot_key, results, vals[key], rule, case=case, step=step, var=var, x=x)
            else:
                results.append(run_expect(root_dot_key, rule, "equal", val=vals[key], case=case, step=step, var=var, x=x))
    if isinstance(rules, list):
        for idx, rule in enumerate(rules):
            root_dot_key = "{}.{}".format(root, idx).lstrip(".")
            if idx >= len(vals):
                results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
            elif isinstance(rule, dict) or isinstance(rule, list):
                if not isinstance(vals[idx], type(rule)):
                    results.append(ExpectResult(is_pass=False, message="TypeDiff", node=root_dot_key, val=vals[idx], expect=rule))
                else:
                    _expect_recursive(root_dot_key, results, vals[idx], rule, case=case, step=step, var=var, x=x)
            else:
                results.append(run_expect(root_dot_key, rule, "equal", val=vals[idx], case=case, step=step, var=var, x=x))


def run_expect(root, rule, func, val=None, case=None, step=None, var=None, x=None):
    if func == "eval":
        ok, res = expect_eval(rule, val=val, case=case, step=step, var=var, x=x)
        if not ok:
            return ExpectResult(is_pass=False, message="NotMatch", node=root, val=val, expect="{} = {}".format(res, rule))
        return ExpectResult(is_pass=True, message="OK", node=root, val=val, expect=rule)
    elif func == "exec":
        ok, res = expect_val_exec(rule, val=val, case=case, step=step, var=var, x=x)
        if not ok:
            return ExpectResult(is_pass=False, message="ExecFail", node=root, val=val, expect="{} = {}".format(res, rule))
        return ExpectResult(is_pass=True, message="OK", node=root, val=val, expect=rule)
    else:
        if val != rule:
            return ExpectResult(is_pass=False, message="NotEqual", node=root, val=val, expect=rule)
        return ExpectResult(is_pass=True, message="OK", node=root, val=val, expect=rule)


def expect_eval(rule, val=None, case=None, step=None, var=None, x=None):
    res = eval(rule)
    if not isinstance(res, bool):
        return res == val, res
    return res, res


def expect_val_exec(rule, val=None, case=None, step=None, var=None, x=None):
    loc = {}
    env = globals()
    env.update(val=val)
    env.update(case=case)
    env.update(step=step)
    env.update(var=var)
    env.update(x=x)
    exec(rule, env, loc)
    res = loc["res"]
    if not isinstance(res, bool):
        return res == val, res
    return res, res
