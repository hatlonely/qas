#!/usr/bin/env python3


from .include import *
from .exec_func import py_exec, py_eval, sh_exec


def render(req, peval="#", pexec="%", pshell="$", **kwargs):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            if key.startswith(peval):
                res[key[len(peval):]] = py_eval(val, **kwargs)
            elif key.startswith(pexec):
                res[key[len(pexec):]] = py_exec(val, **kwargs)
            elif key.startswith(pshell):
                res[key[len(pshell):]] = sh_exec(val)
            else:
                res[key] = render(req[key], **kwargs)
        return res
    if isinstance(req, list):
        res = []
        for val in req:
            res.append(render(val, **kwargs))
        return res
    return req
