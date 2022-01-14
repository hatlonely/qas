#!/usr/bin/env python3


import requests
from src.qas.driver.default import merge, REQUIRED


class HttpDriver:
    endpoint = None
    headers = None
    method = None

    def __init__(self, args: dict):
        args = merge(args, {
            "endpoint": REQUIRED
        })

        self.endpoint = args["endpoint"].rstrip("/")
        if "headers" in args:
            self.headers = args["headers"]
        if "method" in args:
            self.method = args["method"]
        else:
            self.method = "POST"

    def do(self, req: dict):
        if "method" not in req:
            req["method"] = self.method
        if "params" not in req:
            req["params"] = None
        if "headers" not in req:
            req["headers"] = {}
        if "data" not in req:
            req["data"] = None
        if "json" not in req:
            req["json"] = None
        if "path" not in req:
            req["path"] = ""
        if self.headers:
            for key in self.headers:
                req["headers"][key] = self.headers[key]

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
