#!/usr/bin/env python3


import tablestore
import json
from default import merge


class OTSDriver:
    client: tablestore.OTSClient = None

    def __init__(self, args: dict):
        args = merge(args, {
            "Endpoint": "required",
            "AccessKeyId": "required",
            "AccessKeySecret": "required",
            "Instance": "required",
        })

        self.client = tablestore.OTSClient(args["Endpoint"], args["AccessKeyId"], args["AccessKeySecret"], args["Instance"])

    def do(self, req: dict):
        req = merge(req, {
            "Action": "required"
        })

        if req["Action"] == "CreateTable":
            return self.create_table(req)
        elif req["Action"] == "ListTable":
            return self.list_table(req)
        else:
            raise Exception("unsupported action [{}]".format(req["Action"]))

    def list_table(self, req):
        res = self.client.list_table()
        return json.loads(json.dumps(res))

    def create_table(self, req):
        req = merge(req, {
            "TableMeta": {
                "TableName": "required",
                "SchemeEntry": [["required", "required"]]
            },
            "TableOptions": {
                "TimeToLive": -1,
                "MaxVersion": 1,
                "MaxTimeDeviation": 86400,
            }
        })

        res = self.client.create_table(
            table_meta=tablestore.TableMeta(
                table_name=req["TableMeta"]["TableName"],
                schema_of_primary_key=[(i[0], i[1]) for i in req["TableMeta"]["SchemaEntry"]],
                defined_columns=[(i[0], i[1]) for i in req["TableMeta"]["DefinedColumns"]],
            ),
            table_options=tablestore.TableOptions(
                time_to_live=req["TableOptions"]["TimeToLive"],
                max_version=req["TableOptions"]["MaxVersion"],
                max_time_deviation=req["TableOptions"]["MaxTimeDeviation"],
            ),
            reserved_throughput=tablestore.ReservedThroughput(tablestore.CapacityUnit(0, 0))
        )
        return json.loads(json.dumps(res))
