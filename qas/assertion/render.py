#!/usr/bin/env python3


def render(req, case=None):
    if isinstance(req, dict):
        res = {}
        for key, val in req.items():
            if key.startswith("#"):
                res[key.lstrip("#")] = eval(val)
            else:
                res[key] = render(req[key], case=case)
        return res
    if isinstance(req, list):
        res = []
        for val in req:
            res.append(render(val, case=case))
        return res
    return req
