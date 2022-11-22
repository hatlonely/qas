#!/usr/bin/env python3


import re

import alibabacloud_tea_openapi.client
from alibabacloud_tea_openapi import models as open_api_models

from ..util import merge, REQUIRED
from .driver import Driver


product_info = {
    "slb": "alibabacloud_slb20140515",
    "ack": "alibabacloud_cs20151215",
    "rds": "alibabacloud_rds20140815",
    "redis": "alibabacloud_r_kvstore20150101",
    "ecs": "alibabacloud_ecs20140526",
    "vpc": "alibabacloud_vpc20160428",
    "ram": "alibabacloud_ram20150501",
    "sts": "alibabacloud_sts20150401",
    "pds": "alibabacloud_pds20220301",
}


def snake_case(name):
    return re.sub("([A-Z]+[a-z0-9]+)", r"\1_", name).lower()[:-1]


class POPV2Driver(Driver):
    product_id: str
    endpoint: str

    def __init__(self, args: dict):
        args = merge(args, {
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "ProductId": REQUIRED,
            "RegionId": None,
        })

        self.region_id = args["RegionId"]
        self.endpoint = args["Endpoint"].rstrip("/")
        self.access_key_id = args["AccessKeyId"]
        self.access_key_secret = args["AccessKeySecret"]
        self.product_id=args["ProductId"]

    def name(self, req):
        return req["Action"]

    def do(self, req):
        config = open_api_models.Config(
            access_key_id=req["AccessKeyId"] if "AccessKeyId" in req else self.access_key_id,
            access_key_secret=req["AccessKeySecret"] if "AccessKeySecret" in req else self.access_key_secret,
            security_token=req["SecurityToken"] if "SecurityToken" in req else None,
            region_id=req["RegionId"] if "RegionId" in req else self.region_id,
            endpoint=req["Endpoint"] if "Endpoint" in req else self.endpoint,
        )

        try:
            action = req["Action"]
            module_name = product_info[self.product_id]
            module_client = __import__("{}.client".format(module_name), fromlist=["Client"])
            module = __import__(product_info[self.product_id], fromlist=["models"])

            client = getattr(module_client, "Client")(config)

            req = getattr(getattr(module, "models"), "{}Request".format(action))().from_map(req)
            res = getattr(client, snake_case(action))(req)
            return res.to_map()["body"]
        except alibabacloud_tea_openapi.client.UnretryableException as e:
            return {
                "Code": e.inner_exception.code,
                "Message": e.inner_exception.message,
                "Detail": e.inner_exception.data,
            }
        except alibabacloud_tea_openapi.client.TeaException as e:
            return {
                "Code": e.code,
                "Message": e.message,
                "Detail": e.data,
            }
        except Exception as e:
            raise e
