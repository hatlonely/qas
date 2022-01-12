#!/usr/bin/env python3


import requests


class HttpDriver:
    endpoint = None

    def __init__(self, args: dict):
        self.endpoint = args["endpoint"].rstrip("/")

    def do(self, req: dict):
        if "method" not in req:
            req["method"] = "post"
        if "params" not in req:
            req["params"] = None
        if "headers" not in req:
            req["headers"] = None
        if "data" not in req:
            req["data"] = None
        if "json" not in req:
            req["json"] = None
        if "path" not in req:
            req["path"] = ""

        res = requests.request(
            method=req["method"],
            url="{}{}".format(self.endpoint, req["path"]),
            params=req["params"],
            data=req["data"],
            json=req["json"],
            headers=req["headers"],
        )
        return {
            "status": res.status_code,
            "headers": dict(res.headers),
            "json": res.json(),
            "text": res.text,
        }
