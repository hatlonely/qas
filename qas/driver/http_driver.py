#!/usr/bin/env python3


import requests
from .default import merge, REQUIRED


class HttpDriver:
    endpoint = None
    headers = None

    def __init__(self, args: dict):
        args = merge(args, {
            "endpoint": REQUIRED,
            "headers": {},
        })

        self.endpoint = args["endpoint"].rstrip("/")
        self.headers = args["headers"]

    def do(self, req: dict):
        req = merge(req, {
            "endpoint": self.endpoint,
            "method": "POST",
            "headers": {},
            "params": {},
            "data": None,
            "json": None,
            "path": "",
        })
        req["headers"] = self.headers | req["headers"]

        res = requests.request(
            method=req["method"],
            url="{}{}".format(req["endpoint"], req["path"]),
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
