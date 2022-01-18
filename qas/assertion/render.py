#!/usr/bin/env python3


def render(req, case=None, var=None):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            if key.startswith("#"):
                res[key.lstrip("#")] = eval(val)
            else:
                res[key] = render(req[key], case=case, var=var)
        return res
    if isinstance(req, list):
        res = []
        for val in req:
            res.append(render(val, case=case, var=var))
        return res
    return req
