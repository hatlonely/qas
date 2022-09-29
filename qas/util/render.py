#!/usr/bin/env python3


from .include import *
from .exec_func import py_exec, py_eval, sh_exec


class RenderError(Exception):
    pass


def render(__req, peval="#", pexec="%", pshell="$", **kwargs):
    return __render_recurisve("", __req, peval, pexec, pshell, **kwargs)


def __render_recurisve(__root, __req, peval="#", pexec="%", pshell="$", **kwargs):
    if isinstance(__req, dict):
        __res = {}
        for __key, __val in __req.items():
            try:
                if __key.startswith(peval):
                    __res[__key[len(peval):]] = py_eval(__val, **kwargs)
                elif __key.startswith(pexec):
                    __res[__key[len(pexec):]] = py_exec(__val, **kwargs)
                elif __key.startswith(pshell):
                    __res[__key[len(pshell):]] = sh_exec(__val)
                else:
                    __res[__key] = __render_recurisve("{}.{}".format(__root, __key).lstrip("."), __req[__key], **kwargs)
            except RenderError as __e:
                raise __e
            except Exception as __e:
                raise RenderError("render failed. key [{}], err [{}]".format("{}.{}".format(__root, __key).lstrip("."), __e))
        return __res
    if isinstance(__req, list):
        __res = []
        for idx, __val in enumerate(__req):
            __res.append(__render_recurisve("{}[{}]".format(__root, idx).lstrip("."), __val, **kwargs))
        return __res
    return __req
