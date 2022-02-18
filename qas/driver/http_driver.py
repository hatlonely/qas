#!/usr/bin/env python3


import durationpy
import requests
from ..util import merge, REQUIRED
from .driver import Driver


class HttpDriver(Driver):
    endpoint = None

    def __init__(self, args: dict):
        args = merge(args, {
            "endpoint": REQUIRED,
        })

        self.endpoint = args["endpoint"].rstrip("/")

    def name(self, req):
        return req["path"] if "path" in req else "/"

    def do(self, req: dict):
        req = merge(req, {
            "endpoint": self.endpoint,
            "method": "POST",
            "headers": {},
            "params": {},
            "data": None,
            "json": None,
            "path": "",
            "timeout": "1s",
            "allowRedirects": True,
        })

        res = requests.request(
            method=req["method"],
            url="{}{}".format(req["endpoint"], req["path"]),
            params=req["params"],
            data=req["data"],
            json=req["json"],
            headers=req["headers"],
            timeout=durationpy.from_str(req["timeout"]).total_seconds(),
            allow_redirects=req["allowRedirects"],
        )

        body = None
        try:
            body = res.json()
        except Exception as e:
            pass

        return {
            "status": res.status_code,
            "headers": dict(res.headers),
            "json": body,
            "text": res.text,
        }
