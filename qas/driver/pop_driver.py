#!/usr/bin/env python3


import json
import traceback
import aliyunsdkcore.acs_exception.exceptions
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from ..util import merge, REQUIRED
from .driver import Driver


product_to_version = {
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


class POPDriver(Driver):
    client: AcsClient
    endpoint: str
    product_id: str
    method: str
    scheme: str

    def __init__(self, args: dict):
        args = merge(args, {
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "DisableVerify": False,
            "RegionId": "",
        })

        self.endpoint = args["Endpoint"].rstrip("/")
        self.client = AcsClient(args["AccessKeyId"], args["AccessKeySecret"], args["RegionId"], verify=not args["DisableVerify"])
        self.region_id = args["RegionId"]

    def name(self, req):
        return req["Action"]

    def do(self, req: dict):
        req = merge(req, {
            "Action": REQUIRED,
            "Method": "POST",
            "Scheme": "https",
            "ProductId": "",
            "Version": "",
            "RegionId": self.region_id,
            "Endpoint": self.endpoint,
        })

        creq = CommonRequest()
        creq.set_accept_format("json")
        creq.set_method(req["Method"])
        creq.set_protocol_type(req["Scheme"])
        if req["Endpoint"]:
            creq.set_domain(req["Endpoint"])

        if req["Version"]:
            creq.set_version(req["Version"])
        elif req["ProductId"]:
            creq.set_version(product_to_version[req["ProductId"]])
        else:
            raise Exception("unknown Version")

        creq.set_action_name(req["Action"])

        for key in req:
            if key in ["Action", "Version", "ProductId", "Scheme", "Method", "Endpoint"]:
                continue
            creq.add_query_param(key, req[key])

        try:
            res = self.client.do_action_with_exception(creq)
            return json.loads(str(res, encoding='utf-8'))
        except aliyunsdkcore.acs_exception.exceptions.ClientException as e:
            return {
                "Code": e.error_code,
                "Message": e.message,
            }
        except aliyunsdkcore.acs_exception.exceptions.ServerException as e:
            return {
                "Status": e.http_status,
                "Code": e.error_code,
                "Message": e.message,
                "RequestId": e.request_id,
            }
        except Exception as e:
            return {
                "Exception": traceback.format_exc(),
            }
