#!/usr/bin/env python3


import unittest
import tablestore
import json
from .default import merge, REQUIRED


class OTSDriver:
    client: tablestore.OTSClient = None

    def __init__(self, args: dict):
        args = merge(args, {
            "Endpoint": REQUIRED,
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "Instance": REQUIRED,
        })

        self.client = tablestore.OTSClient(args["Endpoint"], args["AccessKeyId"], args["AccessKeySecret"], args["Instance"])

    def do(self, req: dict):
        req = merge(req, {
            "Action": REQUIRED
        })

        do_map = {
            "CreateTable": self.create_table,
            "DeleteTable": self.delete_table,
            "ListTable": self.list_table,
            "GetRow": self.get_row,
            "PutRow": self.put_row,
            "DeleteRow": self.delete_row,
            "GetRange": self.get_range,
        }
        if req["Action"] not in do_map:
            raise Exception("unsupported action [{}]".format(req["Action"]))

        return do_map[req["Action"]](req)

    def list_table(self, req):
        res = self.client.list_table()
        return json.loads(json.dumps(res))

    def create_table(self, req):
        req = merge(req, {
            "TableMeta": {
                "TableName": REQUIRED,
                "SchemaEntry": [{
                    "Name": REQUIRED,
                    "Type": REQUIRED,  # STRING / INTEGER / BOOLEAN / DOUBLE / BINARY
                }],
                "DefinedColumns": []
            },
            "TableOptions": {
                "TimeToLive": -1,
                "MaxVersion": 1,
                "MaxTimeDeviation": 86400,
            }
        })

        self.client.create_table(
            table_meta=tablestore.TableMeta(
                table_name=req["TableMeta"]["TableName"],
                schema_of_primary_key=[(i["Name"], i["Type"]) for i in req["TableMeta"]["SchemaEntry"]],
                defined_columns=[(i["Name"], i["Type"]) for i in req["TableMeta"]["DefinedColumns"]],
            ),
            table_options=tablestore.TableOptions(
                time_to_live=req["TableOptions"]["TimeToLive"],
                max_version=req["TableOptions"]["MaxVersion"],
                max_time_deviation=req["TableOptions"]["MaxTimeDeviation"],
            ),
            reserved_throughput=tablestore.ReservedThroughput(tablestore.CapacityUnit(0, 0))
        )
        return {}

    def delete_table(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
        })
        self.client.delete_table(req["TableName"])
        return {}

    def put_row(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
            "Row": {
                "PrimaryKey": [{
                    "Key": REQUIRED,
                    "Val": REQUIRED,
                }]
            },
            "Condition": "IGNORE",  # IGNORE / EXPECT_EXIST / EXPECT_NOT_EXIST
        })

        _, _ = self.client.put_row(
            table_name=req["TableName"],
            row=tablestore.Row(
                primary_key=[(i["Key"], i["Val"]) for i in req["Row"]["PrimaryKey"]],
                attribute_columns=req["Row"]["AttributeColumns"].items(),
            ),
            condition=tablestore.Condition(req["Condition"])
        )

        return {}

    def get_row(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
            "MaxVersion": 1,
        })

        _, row, _ = self.client.get_row(
            table_name=req["TableName"],
            primary_key=[(i["Key"], i["Val"]) for i in req["PrimaryKey"]],
            max_version=req["MaxVersion"],
        )

        return dict([(i[0], i[1]) for i in row.attribute_columns])

    def delete_row(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
            "PrimaryKey": [{
                "Key": REQUIRED,
                "Val": REQUIRED,
            }],
            "Condition": "IGNORE",  # IGNORE / EXPECT_EXIST / EXPECT_NOT_EXIST
        })

        self.client.delete_row(
            table_name=req["TableName"],
            row=tablestore.Row(
                primary_key=[(i["Key"], i["Val"]) for i in req["PrimaryKey"]],
            ),
            condition=tablestore.Condition(req["Condition"])
        )

        return {}

    def get_range(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
            "Direction": "FORWARD",
            "StartPrimaryKey": [{
                "Key": REQUIRED,
                "Val": tablestore.INF_MIN
            }],
            "EndPrimaryKey": [{
                "Key": REQUIRED,
                "Val": tablestore.INF_MAX,
            }]
        })

        _, _, rows, _ = self.client.get_range(
            table_name=req["TableName"],
            direction=req["Direction"],
            inclusive_start_primary_key=[(i["Key"], pk_val(i["Val"]) if "Val" in i else tablestore.INF_MIN) for i in req["StartPrimaryKey"]],
            exclusive_end_primary_key=[(i["Key"], pk_val(i["Val"]) if "Val" in i else tablestore.INF_MAX) for i in req["EndPrimaryKey"]],
        )

        return [dict([(i[0], i[1]) for i in row.primary_key]) | dict([(i[0], i[1]) for i in row.attribute_columns]) for row in rows]


def pk_val(val):
    if val == "INF_MAX":
        return tablestore.INF_MAX
    if val == "INF_MIN":
        return tablestore.INF_MIN
    return val


