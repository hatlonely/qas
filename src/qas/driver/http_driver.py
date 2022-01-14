#!/usr/bin/env python3


import requests
from src.qas.driver.default import merge, REQUIRED


class HttpDriver:
    endpoint = None
    headers = None
    method = None

    def __init__(self, args: dict):
        args = merge(args, {
            "endpoint": REQUIRED,
            "headers": {},
            "method": "POST"
        })

        self.endpoint = args["endpoint"].rstrip("/")
        self.headers = args["headers"]
        self.method = "POST"

    def do(self, req: dict):
        req = merge(req, {
            "method": self.method,
            "headers": {},
            "params": {},
            "data": None,
            "json": None,
            "path": "",
        })

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
