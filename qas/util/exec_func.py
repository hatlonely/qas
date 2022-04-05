#!/usr/bin/env python3


from .include import *
import subprocess


def py_eval(rule, **kwargs):
    locals().update(**kwargs)
    return eval(rule)


def py_exec(rule, **kwargs):
    loc = {}
    env = locals()
    env.update(**kwargs)
    env.update(to_time=to_time)
    exec(rule, env, loc)
    return loc["res"]


def sh_exec(rule):
    process = subprocess.run(
        ["/bin/bash", "-c", rule],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process.stdout.decode("utf-8")
