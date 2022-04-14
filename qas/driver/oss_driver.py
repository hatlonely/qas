#!/usr/bin/env python3
import copy
import json

import oss2
import re

from ..util import merge, REQUIRED
from .driver import Driver


def pascal_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_pascal(name):
    return name.replace("_", " ").title().replace(" ", "")


class OSSDriver(Driver):
    client: oss2.Bucket

    def __init__(self, args):
        args = merge(args, {
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "Endpoint": REQUIRED,
            "Bucket": REQUIRED,
        })

        self.client = oss2.Bucket(
            oss2.Auth(
                access_key_id=args["AccessKeyId"],
                access_key_secret=args["AccessKeySecret"],
            ),
            endpoint=args["Endpoint"],
            bucket_name=args["Bucket"],
        )

    def name(self, req):
        return req["Action"]

    def do(self, req):
        req = merge(req, {
            "Action": REQUIRED
        })

        try:
            if req["Action"] == "SignURL":
                return self.sign_url(req)
            args = dict((pascal_to_snake(k), v) for k, v in req.items())
            del args["action"]
            res = getattr(self.client, pascal_to_snake(req["Action"]))(**args)
            res = res.__dict__
            del res["resp"]
            res["headers"] = dict([(i, res["headers"][i]) for i in res["headers"]])
            res = dict((snake_to_pascal(k), v) for k, v in res.items())
            return res
        except oss2.exceptions.NoSuchKey as e:
            return {
                "Status": e.status,
                "RequestId": e.request_id,
                "Code": e.code,
                "Message": e.message,
                "Details": e.details,
            }
        except Exception as e:
            raise e

    def sign_url(self, req):
        req = merge(req, {
            "Method": "GET",
            "Key": REQUIRED,
            "Expires": 1800,
            "Headers": None,
            "Params": None,
            "SlashSafe": False,
        })
        res = self.client.sign_url(
            method=req["Method"],
            key=req["Key"],
            expires=req["Expires"],
            headers=req["Headers"],
            params=req["Params"],
            slash_safe=req["SlashSafe"],
        )
        return {
            "DownloadURL": res
        }
