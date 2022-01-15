#!/usr/bin/env python3


import unittest
from ots_driver import *


class TestOTSDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = OTSDriver(args={
            "Endpoint": "https://xx.cn-shanghai.ots.aliyuncs.com",
            "AccessKeyId": "xx",
            "AccessKeySecret": "xx",
            "Instance": "xx",
        })
        self.test_table_name="testQAS"

    def test_list_table(self):
        res = self.driver.do(req={
            "Action": "ListTable"
        })
        print(json.dumps(res))

    def test_crate_table(self):
        res = self.driver.do(req={
            "Action": "CreateTable",
            "TableMeta": {
                "TableName": self.test_table_name,
                "SchemaEntry": [{
                    "Name": "PK1",
                    "Type": "STRING",
                }, {
                    "Name": "PK2",
                    "Type": "STRING",
                }]
            },
            "TableOptions": {
                "TimeToLive": -1,
                "MaxVersion": 1,
                "MaxTimeDeviation": 86400,
            }
        })
        print(json.dumps(res))

    def test_delete_table(self):
        res = self.driver.do(req={
            "Action": "DeleteTable",
            "TableName": self.test_table_name,
        })
        print(json.dumps(res))

    def test_put_row(self):
        res = self.driver.do(req={
            "Action": "PutRow",
            "TableName": self.test_table_name,
            "Row": {
                "PrimaryKey": [{
                    "Key": "PK1",
                    "Val": "pkVal1",
                }, {
                    "Key": "PK2",
                    "Val": "pkVal2"
                }],
                "AttributeColumns": {
                    "key1": "val1",
                    "key2": "val2",
                }
            },
        })
        print(json.dumps(res))

    def test_get_row(self):
        res = self.driver.do(req={
            "Action": "GetRow",
            "TableName": self.test_table_name,
            "PrimaryKey": [{
                "Key": "PK1",
                "Val": "pkVal1",
            }, {
                "Key": "PK2",
                "Val": "pkVal2"
            }]
        })
        print(json.dumps(res))

    def test_delete_row(self):
        res = self.driver.do(req={
            "Action": "DeleteRow",
            "TableName": self.test_table_name,
            "PrimaryKey": [{
                "Key": "PK1",
                "Val": "pkVal1",
            }, {
                "Key": "PK2",
                "Val": "pkVal2"
            }]
        })
        print(json.dumps(res))

    def test_get_range(self):
        res = self.driver.do(req={
            "Action": "GetRange",
            "TableName": self.test_table_name,
            "StartPrimaryKey": [{
                "Key": "PK1",
            }, {
                "Key": "PK2",
            }],
            "EndPrimaryKey": [{
                "Key": "PK1",
            }, {
                "Key": "PK2",
            }]
        })
        print(json.dumps(res))


if __name__ == '__main__':
    unittest.main()
