#!/usr/bin/env python3


from datetime import datetime
from aliyun.log import LogClient, PutLogsRequest, LogItem, GetLogsRequest

from ..util import merge, REQUIRED
from .driver import Driver


class SLSDriver(Driver):
    def __init__(self, args):
        args = merge(args, {
            "Endpoint": REQUIRED,
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
        })

        self.client = LogClient(
            args["Endpoint"],
            args["AccessKeyId"],
            args["AccessKeySecret"],
        )

    def name(self, req):
        return req["Action"]

    def do(self, req: dict):
        req = merge(req, {
            "Action": REQUIRED
        })

        do_map = {
            "GetLogs": self.get_logs,
            "PutLogs": self.put_logs,
        }

        if req["Action"] not in do_map:
            raise Exception("unsupported action [{}]".format(req["Action"]))

        try:
            return do_map[req["Action"]](req)
        except Exception as e:
            raise e

    def get_logs(self, req):
        req = merge(req, {
            "Project": REQUIRED,
            "Logstore": REQUIRED,
            "FromTime": int(datetime.now().timestamp()) - 3600,
            "ToTime": int(datetime.now().timestamp()),
            "Topic": None,
            "Query": None,
            "Offset": 0,
            "Size": 100,
            "Reverse": False,
            "PowerSQL": False,
        })

        res = self.client.get_logs(GetLogsRequest(
            project=req["Project"],
            logstore=req["Logstore"],
            fromTime=req["FromTime"],
            toTime=req["ToTime"],
            topic=req["Topic"],
            query=req["Query"],
            line=req["Size"],
            offset=req["Offset"],
            reverse=req["Reverse"],
            power_sql=req["PowerSQL"],
        ))

        return {
            "RequestId": res.get_request_id(),
            "Header": res.headers,
            "Body": res.body,
        }

    def put_logs(self, req):
        req = merge(req, {
            "Project": REQUIRED,
            "Logstore": REQUIRED,
            "Topic": None,
            "Source": None,
            "HashKey": None,
            "Compress": False,
            "LogTags": {},
            "LogItems": [{
                "Timestamp": int(datetime.now().timestamp()),
                "Contents": {},
            }]
        })

        res = self.client.put_logs(PutLogsRequest(
            project=req["Project"],
            logstore=req["Logstore"],
            topic=req["Topic"],
            source=req["Source"],
            hashKey=req["HashKey"],
            compress=req["Compress"],
            logtags=req["LogTags"].items(),
            logitems=[
                LogItem(
                    timestamp=item["Timestamp"],
                    contents=[(k, v) for k, v in item["Contents"].items()],
                )
                for item in req["LogItems"]
            ]
        ))

        return {
            "RequestId": res.get_request_id(),
            "Header": res.headers,
            "Body": res.get_body(),
        }
