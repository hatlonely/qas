#!/usr/bin/env python3


from .include import *
from .exec_with_res import exec_with_res


def render(req, case=None, var=None, x=None, peval="#", pexec="%"):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            if key.startswith(peval):
                res[key[len(peval):]] = eval(val)
            elif key.startswith(pexec):
                res[key[len(pexec):]] = exec_with_res(val, case=case, var=var, x=x)
            else:
                res[key] = render(req[key], case=case, var=var, x=x)
        return res
    if isinstance(req, list):
        res = []
        for val in req:
            res.append(render(val, case=case, var=var, x=x))
        return res
    return req
