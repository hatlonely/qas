#!/usr/bin/env python3


from .include import *


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
