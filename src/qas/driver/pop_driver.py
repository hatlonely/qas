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
    Endpoint: str
    ProductId: str

    def __init__(self, args: dict):
        if "AccessKeyId" not in args:
            raise Exception("AccessKeyId is required")
        if "AccessKeySecret" not in args:
            raise Exception("AccessKeySecret is required")
        if "RegionId" not in args:
            args["RegionId"] = ""
        if "DisableVerify" not in args:
            args["DisableVerify"] = False
        self.Endpoint = args["Endpoint"].rstrip("/")
        self.client = AcsClient(args["AccessKeyId"], args["AccessKeySecret"], args["RegionId"], verify=args["DisableVerify"])
        if "ProductId" in args:
            self.ProductId = args["ProductId"]

    def do(self, req: dict):
        if "Method" not in req:
            req["Method"] = "POST"
        if "Scheme" not in req:
            req["Scheme"] = "https"
        if "Action" not in req:
            raise Exception("Action is required")
        if "ProductId" not in req and self.ProductId:
            req["ProductId"] = self.ProductId
        if "Endpoint" not in req:
            req["Endpoint"] = self.Endpoint

        creq = CommonRequest()
        creq.set_accept_format("json")
        creq.set_method(req["Method"])
        creq.set_protocol_type(req["Scheme"])
        if "Endpoint" in req:
            creq.set_domain(req["Endpoint"])
        elif self.Endpoint:
            creq.set_domain(self.Endpoint)

        if "Version" in req:
            creq.set_version(req["Version"])
        elif "ProductId" in req:
            creq.set_version(product_info[req["ProductId"]])
        else:
            raise Exception("unknown Version")

        creq.set_action_name(req["Action"])

        for key in req:
            if key in ["Action", "Version", "ProductId", "Scheme", "Method"]:
                continue
            creq.add_query_param(key, req[key])

        res = self.client.do_action_with_exception(creq)
        return json.loads(str(res, encoding='utf-8'))
