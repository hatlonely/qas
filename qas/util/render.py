#!/usr/bin/env python3


from .include import *
from .exec_func import exec_with_kw, eval_with_kw, exec_shell


def render(req, peval="#", pexec="%", pshell="$", **kwargs):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            if key.startswith(peval):
                res[key[len(peval):]] = eval_with_kw(val, **kwargs)
            elif key.startswith(pexec):
                res[key[len(pexec):]] = exec_with_kw(val, **kwargs)
            elif key.startswith(pshell):
                res[key[len(pshell):]] = exec_shell(val)
            else:
                res[key] = render(req[key], **kwargs)
        return res
    if isinstance(req, list):
        res = []
        for val in req:
            res.append(render(val, **kwargs))
        return res
    return req
