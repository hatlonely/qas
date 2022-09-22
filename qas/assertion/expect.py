#!/usr/bin/env python3


from ..result import ExpectResult, AssertResult
from ..util.include import *
from ..util import py_exec, py_eval
import traceback


def expect(vals, rules, peval="#", pexec="%", mode="", **kwargs):
    if mode == peval:
        return [run_expect("", rules, "eval", val=vals, **kwargs)]
    if mode == pexec:
        return [run_expect("", rules, "exec", val=vals, **kwargs)]

    if not rules:
        return []

    results = []
    __expect_recursive("", results, vals, rules, peval=peval, pexec=pexec, **kwargs)
    return results


def __expect_recursive(root: str, results: list[ExpectResult], vals, rules, peval="#", pexec="%", **kwargs):
    if isinstance(rules, dict):
        for key, rule in rules.items():
            root_dot_key = "{}.{}".format(root, key.lstrip(peval).lstrip(pexec)).lstrip(".")
            if key.startswith(pexec):
                if key[len(pexec):] not in vals:
                    results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
                else:
                    results.append(run_expect(root_dot_key, rule, "exec", val=vals[key[len(pexec):]], **kwargs))
            elif key.startswith(peval):
                if key[len(peval):] not in vals:
                    results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
                else:
                    results.append(run_expect(root_dot_key, rule, "eval", val=vals[key[len(peval):]], **kwargs))
            elif key not in vals:
                results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
            elif isinstance(rule, dict) or isinstance(rule, list):
                if not isinstance(vals[key], type(rule)):
                    results.append(ExpectResult(is_pass=False, message="TypeDiff", node=root_dot_key, val=vals[key], expect=rule))
                else:
                    __expect_recursive(root_dot_key, results, vals[key], rule, peval=peval, pexec=pexec, **kwargs)
            else:
                results.append(run_expect(root_dot_key, rule, "equal", val=vals[key], **kwargs))
    elif isinstance(rules, list):
        for idx, rule in enumerate(rules):
            root_dot_key = "{}.{}".format(root, idx).lstrip(".")
            if idx >= len(vals):
                results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=root_dot_key, val=None, expect=rule))
            elif isinstance(rule, dict) or isinstance(rule, list):
                if not isinstance(vals[idx], type(rule)):
                    results.append(ExpectResult(is_pass=False, message="TypeDiff", node=root_dot_key, val=vals[idx], expect=rule))
                else:
                    __expect_recursive(root_dot_key, results, vals[idx], rule, peval=peval, pexec=pexec, **kwargs)
            else:
                results.append(run_expect(root_dot_key, rule, "equal", val=vals[idx], **kwargs))
    else:
        if vals == rules:
            results.append(ExpectResult(is_pass=True, message="OK", node=root, val=vals, expect=rules))
        else:
            results.append(ExpectResult(is_pass=False, message="NotEqual", node=root, val=vals, expect=rules))


def run_expect(root, rule, func, val=None, **kwargs):
    if func == "eval":
        ok, res = expect_eval(rule, val=val, **kwargs)
        if not ok:
            return ExpectResult(is_pass=False, message="EvalFail", node=root, val=val, expect="{} = {}".format(res, rule))
        return ExpectResult(is_pass=True, message="OK", node=root, val=val, expect=rule)
    elif func == "exec":
        ok, res = expect_exec(rule, val=val, **kwargs)
        if not ok:
            return ExpectResult(is_pass=False, message="ExecFail", node=root, val=val, expect="{} = {}".format(res, rule))
        return ExpectResult(is_pass=True, message="OK", node=root, val=val, expect=rule)
    else:
        if val != rule:
            return ExpectResult(is_pass=False, message="NotEqual", node=root, val=val, expect=rule)
        return ExpectResult(is_pass=True, message="OK", node=root, val=val, expect=rule)


def expect_eval(rule, val=None, **kwargs):
    res = py_eval(rule, val=val, **kwargs)
    if not isinstance(res, bool):
        return res == val, res
    return res, res


def expect_exec(rule, val=None, **kwargs):
    res = py_exec(rule, val=val, **kwargs)
    if not isinstance(res, bool):
        return res == val, res
    return res, res


def check(rule, val=None, **kwargs):
    ok, res = expect_eval(rule, val=val, **kwargs)
    return ok


def assert_(rules, **kwargs):
    results = list[AssertResult]()
    for rule in rules:
        try:
            ok = check(rule, **kwargs)
            results.append(AssertResult(is_pass=ok, rule=rule, message=""))
        except Exception as e:
            results.append(AssertResult(is_pass=False, rule=rule, message="Exception: {}".format(e)))
    return results
