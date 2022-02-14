#!/usr/bin/env python3


from .include import *


def render(req, case=None, var=None, x=None, peval="#", pexec="%"):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            if key.startswith(peval):
                res[key.lstrip(peval)] = eval(val)
            else:
                res[key] = render(req[key], case=case, var=var, x=x)
        return res
    if isinstance(req, list):
        res = []
        for val in req:
            res.append(render(val, case=case, var=var, x=x))
        return res
    return req
