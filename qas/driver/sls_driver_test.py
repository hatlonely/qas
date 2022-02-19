#!/usr/bin/env python3


import datetime
import json
import unittest
from aliyun.log import LogClient, PutLogsRequest, LogItem, GetLogsRequest

from .sls_driver import SLSDriver


class TestSLS(unittest.TestCase):
    def test_sls(self):
        client = LogClient(
            "cn-shanghai.log.aliyuncs.com",
            "xx",
            "xx",
        )

        res = client.put_logs(PutLogsRequest(
            project="imm-dev-hl",
            logstore="convert-server-log",
            topic="test-topic",
            source="test-source",
            hashKey="123123",
            logtags=[("tag1", "val1"), ("tag2", "val2")],
            logitems=[
                LogItem(
                    timestamp=int(datetime.datetime.now().timestamp()),
                    contents=[
                        ("key1", "val1"),
                        ("key2", "val2"),
                    ],
                ),
                LogItem(
                    timestamp=int(datetime.datetime.now().timestamp()),
                    contents=[
                        ("key3", "val3"),
                        ("key4", "val4"),
                    ],
                )
            ],
        ))
        print(res)

        res = client.get_logs(GetLogsRequest(
            project="imm-dev-hl",
            logstore="convert-server-log",
            fromTime=int(datetime.datetime.now().timestamp()) - 3600,
            toTime=int(datetime.datetime.now().timestamp()),
            topic="test-topic",
        ))
        print(res)


class TestSLSDriver(unittest.TestCase):
    def test_sls_driver(self):
        driver = SLSDriver({
            "Endpoint": "cn-shanghai.log.aliyuncs.com",
            "AccessKeyId": "xx",
            "AccessKeySecret": "xx",
        })

        res = driver.do({
            "Action": "PutLogs",
            "Project": "imm-dev-hl",
            "Logstore": "convert-server-log",
            "Topic": "test-topic",
            "Source": "test-source",
            "HashKey": "123123",
            "LogTags": {
                "tag1": "val1",
                "tag2": "val2",
            },
            "LogItems": [{
                "Timestamp": int(datetime.datetime.now().timestamp()),
                "Contents": {
                    "key1": "val1",
                    "key2": "val2",
                    "key3": "val3",
                }
            }],
        })
        print(json.dumps(res, indent=2))

        res = driver.do({
            "Action": "GetLogs",
            "Project": "imm-dev-hl",
            "Logstore": "convert-server-log",
            "FromTime": int(datetime.datetime.now().timestamp()) - 3600,
            "ToTime": int(datetime.datetime.now().timestamp()),
            "Topic": "test-topic"
        })
        print(json.dumps(res, indent=2))


def main():
    unittest.main()


if __name__ == "__main__":
    main()
