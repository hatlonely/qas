#!/usr/bin/env python3


from .include import *
import subprocess


def eval_with_kw(rule, **kwargs):
    locals().update(**kwargs)
    return eval(rule)


def exec_with_kw(rule, **kwargs):
    loc = {}
    env = locals()
    env.update(**kwargs)
    env.update(to_time=to_time)
    exec(rule, env, loc)
    return loc["res"]


def exec_shell(rule):
    process = subprocess.run(
        ["/bin/bash", "-c", rule],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process.stdout.decode("utf-8")
