#!/usr/bin/env python3


from ..result import ExpectResult, AssertResult
from ..util.include import *
from ..util import py_exec, py_eval
import traceback


def expect(__vals, __rules, peval="#", pexec="%", mode="", **kwargs):
    if mode == peval:
        return [run_expect("", __rules, "eval", val=__vals, **kwargs)]
    if mode == pexec:
        return [run_expect("", __rules, "exec", val=__vals, **kwargs)]

    if not __rules:
        return []

    __results = []
    __expect_recursive("", __results, __vals, __rules, peval=peval, pexec=pexec, **kwargs)
    return __results


def __expect_recursive(__root: str, __results: list[ExpectResult], __vals, __rules, peval="#", pexec="%", **kwargs):
    if isinstance(__rules, dict):
        for __key, __rule in __rules.items():
            __root_dot_key = "{}.{}".format(__root, __key.lstrip(peval).lstrip(pexec)).lstrip(".")
            if __key.startswith(pexec):
                if __key[len(pexec):] not in __vals:
                    __results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=__root_dot_key, val=None, expect=__rule))
                else:
                    __results.append(run_expect(__root_dot_key, __rule, "exec", val=__vals[__key[len(pexec):]], **kwargs))
            elif __key.startswith(peval):
                if __key[len(peval):] not in __vals:
                    __results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=__root_dot_key, val=None, expect=__rule))
                else:
                    __results.append(run_expect(__root_dot_key, __rule, "eval", val=__vals[__key[len(peval):]], **kwargs))
            elif __key not in __vals:
                __results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=__root_dot_key, val=None, expect=__rule))
            elif isinstance(__rule, dict) or isinstance(__rule, list):
                if not isinstance(__vals[__key], type(__rule)):
                    __results.append(ExpectResult(is_pass=False, message="TypeDiff", node=__root_dot_key, val=__vals[__key], expect=__rule))
                else:
                    __expect_recursive(__root_dot_key, __results, __vals[__key], __rule, peval=peval, pexec=pexec, **kwargs)
            else:
                __results.append(run_expect(__root_dot_key, __rule, "equal", val=__vals[__key], **kwargs))
    elif isinstance(__rules, list):
        for __idx, __rule in enumerate(__rules):
            __root_dot_key = "{}.{}".format(__root, __idx).lstrip(".")
            if __idx >= len(__vals):
                __results.append(ExpectResult(is_pass=False, message="NoSuchKey", node=__root_dot_key, val=None, expect=__rule))
            elif isinstance(__rule, dict) or isinstance(__rule, list):
                if not isinstance(__vals[__idx], type(__rule)):
                    __results.append(ExpectResult(is_pass=False, message="TypeDiff", node=__root_dot_key, val=__vals[__idx], expect=__rule))
                else:
                    __expect_recursive(__root_dot_key, __results, __vals[__idx], __rule, peval=peval, pexec=pexec, **kwargs)
            else:
                __results.append(run_expect(__root_dot_key, __rule, "equal", val=__vals[__idx], **kwargs))
    else:
        if __vals == __rules:
            __results.append(ExpectResult(is_pass=True, message="OK", node=__root, val=__vals, expect=__rules))
        else:
            __results.append(ExpectResult(is_pass=False, message="NotEqual", node=__root, val=__vals, expect=__rules))


def run_expect(__root, __rule, func, val=None, **kwargs):
    if func == "eval":
        ok, __res = expect_eval(__rule, val=val, **kwargs)
        if not ok:
            return ExpectResult(is_pass=False, message="EvalFail", node=__root, val=val, expect="{} = {}".format(__res, __rule))
        return ExpectResult(is_pass=True, message="OK", node=__root, val=val, expect=__rule)
    elif func == "exec":
        ok, __res = expect_exec(__rule, val=val, **kwargs)
        if not ok:
            return ExpectResult(is_pass=False, message="ExecFail", node=__root, val=val, expect="{} = {}".format(__res, __rule))
        return ExpectResult(is_pass=True, message="OK", node=__root, val=val, expect=__rule)
    else:
        if val != __rule:
            return ExpectResult(is_pass=False, message="NotEqual", node=__root, val=val, expect=__rule)
        return ExpectResult(is_pass=True, message="OK", node=__root, val=val, expect=__rule)


def expect_eval(__rule, val=None, **kwargs):
    __res = py_eval(__rule, val=val, **kwargs)
    if not isinstance(__res, bool):
        return __res == val, __res
    return __res, __res


def expect_exec(__rule, val=None, **kwargs):
    __res = py_exec(__rule, val=val, **kwargs)
    if not isinstance(__res, bool):
        return __res == val, __res
    return __res, __res


def check(__rule, val=None, **kwargs):
    if isinstance(__rule, list):
        for __x in __rule:
            if not check(__x, val=val, **kwargs):
                return False
        return True
    ok, __res = expect_eval(__rule, val=val, **kwargs)
    return ok


def assert_(__rules, **kwargs):
    __results = list[AssertResult]()
    for __rule in __rules:
        try:
            ok = check(__rule, **kwargs)
            __results.append(AssertResult(is_pass=ok, rule=__rule, message=""))
        except Exception as e:
            __results.append(AssertResult(is_pass=False, rule=__rule, message="Exception: {}".format(e)))
    return __results
