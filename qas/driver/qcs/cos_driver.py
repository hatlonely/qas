#!/usr/bin/env python3


import copy
import re
import json

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import qcloud_cos.cos_exception

from ..driver import Driver
from ...util import merge, REQUIRED


def pascal_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_pascal(name):
    return name.replace("_", " ").title().replace(" ", "")


# https://cloud.tencent.com/document/product/436/12269
class COSDriver(Driver):
    def __init__(self, args):
        client: CosS3Client
        bucket: str

        args = merge(args, {
            "SecretId": REQUIRED,
            "SecretKey": REQUIRED,
            "Region": REQUIRED,
            "Bucket": "",
        })
        self.client = CosS3Client(CosConfig(
            Region=args["Region"],
            SecretId=args["SecretId"],
            SecretKey=args["SecretKey"],
            Token=None,
            Scheme="https",
        ))
        self.bucket = args["Bucket"]

    def name(self, req):
        return req["Action"]

    def do(self, req: dict):
        req = merge(req, {
            "Action": REQUIRED,
            "Bucket": self.bucket
        })

        try:
            args = copy.deepcopy(req)
            del args["Action"]
            res = getattr(self.client, pascal_to_snake(req["Action"]))(**args)
            res = json.loads(json.dumps(res, default=lambda x: dict((snake_to_pascal(k), v) for k, v in x.__dict__.items())))
            return res
        except qcloud_cos.cos_exception.CosServiceError as e:
            return {
                "Status": e.get_status_code(),
                "RequestId": e.get_request_id(),
                "Code": e.get_error_code(),
                "Message": e.get_error_msg(),
                "OriginMessage": e.get_origin_msg(),
            }
        except Exception as e:
            raise e
