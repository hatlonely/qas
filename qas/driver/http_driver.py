#!/usr/bin/env python3


import durationpy
import requests
import hashlib
from ..util import merge, REQUIRED
from .driver import Driver
from urllib.parse import urlparse


class HttpDriver(Driver):
    endpoint = None

    def __init__(self, args: dict):
        args = merge(args, {
            "endpoint": "",
        })

        self.endpoint = args["endpoint"].rstrip("/")

    def name(self, req):
        if req["url"]:
            return urlparse(req["url"]).path
        return req["path"] if "path" in req else "/"

    def do(self, req: dict):
        req = merge(req, {
            "url": "",
            "endpoint": self.endpoint,
            "method": "POST",
            "headers": {},
            "params": {},
            "data": None,
            "json": None,
            "path": "",
            "timeout": "1s",
            "allowRedirects": True,
            "md5Only": False,
        })

        if req["md5Only"]:
            return self.do_md5only(req)

        res = requests.request(
            method=req["method"],
            url=req["url"] if req["url"] else "{}{}".format(req["endpoint"], req["path"]),
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

    def do_md5only(self, req: dict):
        res = requests.request(
            method=req["method"],
            url="{}{}".format(req["endpoint"], req["path"]),
            params=req["params"],
            data=req["data"],
            json=req["json"],
            headers=req["headers"],
            timeout=durationpy.from_str(req["timeout"]).total_seconds(),
            allow_redirects=req["allowRedirects"],
            stream=True,
        )

        md5 = ""
        if res.status_code == 200:
            h = hashlib.new("md5")
            for chunk in res:
                h.update(chunk)
            md5 = h.hexdigest()

        return {
            "status": res.status_code,
            "headers": dict(res.headers),
            "md5": md5
        }

