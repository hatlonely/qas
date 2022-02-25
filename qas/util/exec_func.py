#!/usr/bin/env python3


from .include import *
import subprocess


def exec_with_res(rule, val=None, case=None, step=None, var=None, x=None):
    loc = {}
    env = globals()
    env.update(val=val)
    env.update(case=case)
    env.update(step=step)
    env.update(var=var)
    env.update(x=x)
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
