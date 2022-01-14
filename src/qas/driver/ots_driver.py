#!/usr/bin/env python3


import tablestore
import json
from src.qas.driver.default import merge, REQUIRED


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
            "ListTable": self.list_table,
            "GetRow": self.get_row,
            "PutRow": self.put_row,
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
                "SchemeEntry": [
                    {
                        "Name": REQUIRED,
                        "Type": REQUIRED,  # STRING / INTEGER / BOOLEAN / DOUBLE / BINARY
                    }
                ]
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
        return json.loads(json.dumps(res))

    def put_row(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
            "Row": {
                "PrimaryKey": [
                    {
                        "Key": REQUIRED,
                        "Val": REQUIRED,
                    }
                ]
            },
            "Condition": "IGNORE",  # IGNORE / EXPECT_EXIST / EXPECT_NOT_EXIST
        })

        consumed, return_row = self.client.put_row(
            table_name=req["TableName"],
            row=tablestore.Row(
                primary_key=[(i["Key"], i["Val"]) for i in req["Row"]["PrimaryKey"]],
                attribute_columns=req["AttributeColumns"],
            ),
            condition=tablestore.Condition(req["Condition"])
        )

        return {
            "Consumed": consumed,
            "ReturnRow": return_row,
        }

    def get_row(self, req):
        req = merge(req, {
            "TableName": REQUIRED,
            "MaxVersion": 1,
        })

        consumed, return_row, next_token = self.client.get_row(
            table_name=req["TableName"],
            primary_key=[(i["Key"], i["Val"]) for i in req["Row"]["PrimaryKey"]],
            max_version=req["MaxVersion"],
        )

        return {
            "Consumed": consumed,
            "ReturnRow": return_row,
            "NextToken": next_token,
        }