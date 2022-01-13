#!/usr/bin/env python3


import tablestore
import json


class OTSDriver:
    client: tablestore.OTSClient = None

    def __init__(self, args: dict):
        self.client = tablestore.OTSClient(args["Endpoint"], args["AccessKeyId"], args["AccessKeySecret"], args["Instance"])

    def do(self, req: dict):
        if "Action" not in req:
            raise Exception("Action is required")

        if req["Action"] == "CreateTable":
            return self.create_table(req)

    def list_table(self):
        res = self.client.list_table()
        return json.loads(json.dumps(res))

    def create_table(self, req):
        if "TableMeta" not in req:
            raise Exception("TableMeta is required")
        if "TableName" not in req["TableMeta"]:
            raise Exception("TableMeta.TableName is required")
        if "SchemeEntry" not in req["TableMeta"]:
            raise Exception("TableMeta.SchemeEntry is required")
        if "TableOptions" not in req:
            req["TableOptions"] = {}
        if "TimeToLive" not in req["TableOptions"]:
            req["TableOptions"]["TimeToLive"] = -1
        if "MaxVersion" not in req["TableOptions"]:
            req["TableOptions"]["MaxVersion"] = 1
        if "MaxTimeDeviation" not in req["TableOptions"]:
            req["TableOptions"]["MaxTimeDeviation"] = 86400

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