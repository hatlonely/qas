#!/usr/bin/env python3


import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


product_info = {
    "ots": "2016-06-20",
    "imm": "2017-09-06",
    "ram": "2015-05-01",
    "slb": "2014-05-15",
    "ack": "2015-12-15",
    "rds": "2014-08-15",
    "redis": "2015-01-01",
    "ecs": "2014-05-26",
    "vpc": "2016-04-28",
    "kms": "2016-01-20",
    "sts": "2015-04-01",
    "immv2": "2020-09-30"
}


class POPDriver:
    client: AcsClient
    endpoint: str

    def __init__(self, args: dict):
        if "accessKeyId" not in args:
            raise Exception("accessKeyId is required")
        if "accessKeySecret" not in args:
            raise Exception("accessKeySecret is required")
        if "regionId" not in args:
            args["regionId"] = ""
        if "disableVerify" not in args:
            args["disableVerify"] = False
        self.endpoint = args["endpoint"].rstrip("/")
        self.client = AcsClient(args["accessKeyId"], args["accessKeySecret"], args["regionId"], verify=args["disableVerify"])

    def do(self, req: dict):
        if "method" not in req:
            req["method"] = "POST"
        if "scheme" not in req:
            req["scheme"] = "https"
        if "action" not in req:
            raise Exception("action is required")

        req = CommonRequest()
        req.set_accept_format("json")
        req.set_method(req["method"])
        req.set_protocol_type(req["scheme"])
        if "endpoint" in req:
            req.set_domain(req["endpoint"])
        elif self.endpoint:
            req.set_domain(self.endpoint)

        if "version" in req:
            req.set_version(req["version"])
        elif "productId" in req:
            req.set_version(product_info[req["productId"]])

        req.set_action_name(req["action"])

        for key in req:
            req.add_query_param(key, req[key])

        res = self.client.do_action_with_exception(req)
        return json.loads(str(res, encoding='utf-8'))
