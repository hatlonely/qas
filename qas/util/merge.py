#!/usr/bin/env python3


REQUIRED = "__DEFAULT__REQUIRED__"


def merge(req, dft):
    if req == None:
        return _merge_recursive("", {}, dft)
    return _merge_recursive("", req, dft)


def _merge_recursive(root: str, req, dft):
    if isinstance(dft, dict):
        for key, val in dft.items():
            root_dot_key = "{}.{}".format(root, key).lstrip(".")
            if isinstance(val, dict):
                req[key] = _merge_recursive(root_dot_key, req[key] if key in req and req[key] is not None else {}, val)
            elif isinstance(val, list):
                req[key] = _merge_recursive(root_dot_key, req[key] if key in req and req[key] is not None else [], val)
            else:
                if val == REQUIRED and key not in req:
                    raise Exception("missing required key [{}]".format(root_dot_key))
                elif key not in req:
                    req[key] = val
    if isinstance(dft, list):
        for idx, val in enumerate(dft):
            root_dot_key = "{}.{}".format(root, idx).lstrip(".")
            if isinstance(val, dict):
                while idx >= len(req):
                    req.append({})
                req[idx] = _merge_recursive(root_dot_key, req[idx], val)
            elif isinstance(val, list):
                while idx >= len(req):
                    req.append([])
                req[idx] = _merge_recursive(root_dot_key, req[idx], val)
            else:
                if val == REQUIRED and idx >= len(req):
                    raise Exception("missing required key [{}]".format(root_dot_key))
                elif idx >= len(req):
                    req.append(val)
    return req
