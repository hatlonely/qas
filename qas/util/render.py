#!/usr/bin/env python3


from .include import *
from .exec_func import py_exec, py_eval, sh_exec


class RenderError(Exception):
    pass


def render(__req, peval="#", pexec="%", pshell="$", **kwargs):
    return __render_recurisve("", __req, **kwargs)


def __render_recurisve(root, __req, peval="#", pexec="%", pshell="$", **kwargs):
    if isinstance(__req, dict):
        __res = {}
        for key, val in __req.items():
            try:
                if key.startswith(peval):
                    __res[key[len(peval):]] = py_eval(val, **kwargs)
                elif key.startswith(pexec):
                    __res[key[len(pexec):]] = py_exec(val, **kwargs)
                elif key.startswith(pshell):
                    __res[key[len(pshell):]] = sh_exec(val)
                else:
                    __res[key] = __render_recurisve("{}.{}".format(root, key).lstrip("."), __req[key], **kwargs)
            except RenderError as e:
                raise e
            except Exception as e:
                raise RenderError("render failed. key [{}], err [{}]".format("{}.{}".format(root, key).lstrip("."), e))
        return __res
    if isinstance(__req, list):
        __res = []
        for idx, val in enumerate(__req):
            __res.append(__render_recurisve("{}[{}]".format(root, idx).lstrip("."), val, **kwargs))
        return __res
    return __req
