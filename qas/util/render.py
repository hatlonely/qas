#!/usr/bin/env python3


from .include import *
from .exec_func import py_exec, py_eval, sh_exec


class RenderError(Exception):
    pass


def render(req, peval="#", pexec="%", pshell="$", **kwargs):
    return _render_recurisve("", req, **kwargs)


def _render_recurisve(root, req, peval="#", pexec="%", pshell="$", **kwargs):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            try:
                if key.startswith(peval):
                    res[key[len(peval):]] = py_eval(val, **kwargs)
                elif key.startswith(pexec):
                    res[key[len(pexec):]] = py_exec(val, **kwargs)
                elif key.startswith(pshell):
                    res[key[len(pshell):]] = sh_exec(val)
                else:
                    res[key] = _render_recurisve("{}.{}".format(root, key).lstrip("."), req[key], **kwargs)
            except RenderError as e:
                raise e
            except Exception as e:
                raise RenderError("render failed. key [{}], err [{}]".format("{}.{}".format(root, key).lstrip("."), e))
        return res
    if isinstance(req, list):
        res = []
        for idx, val in enumerate(req):
            res.append(_render_recurisve("{}[{}]".format(root, idx).lstrip("."), val, **kwargs))
        return res
    return req
