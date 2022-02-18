#!/usr/bin/env python3


import oss2

from ..util import merge, REQUIRED
from .driver import Driver


class OSSDriver(Driver):
    client: oss2.Bucket

    def __init__(self, args):
        args = merge(args, {
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "Endpoint": REQUIRED,
            "Bucket": REQUIRED,
        })

        self.client = oss2.Bucket(
            oss2.Auth(
                access_key_id=args["AccessKeyId"],
                access_key_secret=args["AccessKeySecret"],
            ),
            endpoint=args["Endpoint"],
            bucket_name=args["Bucket"],
        )

    def name(self, req):
        return req["Action"]

    def do(self, req):
        req = merge(req, {
            "Action": REQUIRED
        })

        do_map = {
            "GetObjectMeta": self.get_object_meta,
            "GetObjectToFile": self.get_object_to_file,
            "PutObjectFromFile": self.put_object_from_file,
            "SignURL": self.sign_url,
        }
        if req["Action"] not in do_map:
            raise Exception("unsupported action [{}]".format(req["Action"]))

        try:
            return do_map[req["Action"]](req)
        except oss2.exceptions.NoSuchKey as e:
            return {
                "Status": e.status,
                "RequestId": e.request_id,
                "Code": e.code,
                "Message": e.message,
                "Details": e.details,
            }
        except Exception as e:
            raise e

    def get_object_meta(self, req):
        req = merge(req, {
            "Key": REQUIRED,
            "Headers": None,
            "Params": None,
        })
        res = self.client.get_object_meta(key=req["Key"], params=req["Params"], headers=req["Headers"])
        return {
            "Status": res.status,
            "Headers": dict([(i, res.headers[i]) for i in res.headers]),
            "RequestId": res.request_id,
            "Etag": res.etag,
            "ContentLength": res.content_length,
            "LastModified": res.last_modified,
            "VersionId": res.versionid,
            "DeleteMarker": res.delete_marker,
        }

    def get_object_to_file(self, req):
        req = merge(req, {
            "Key": REQUIRED,
            "Filename": REQUIRED,
            "Headers": None,
            "Params": None,
        })
        res = self.client.get_object_to_file(
            key=req["Key"],
            filename=req["Filename"],
            headers=req["Headers"],
            params=req["Params"],
        )
        return {
            "Status": res.status,
            "Headers": dict([(i, res.headers[i]) for i in res.headers]),
            "RequestId": res.request_id,
            "Etag": res.etag,
            "ContentLength": res.content_length,
            "LastModified": res.last_modified,
            "VersionId": res.versionid,
            "DeleteMarker": res.delete_marker,
        }

    def put_object_from_file(self, req):
        req = merge(req, {
            "Key": REQUIRED,
            "Filename": REQUIRED,
            "Headers": None,
        })
        res = self.client.put_object_from_file(
            key=req["Key"],
            filename=req["Filename"],
            headers=req["Headers"],
        )
        return {
            "Status": res.status,
            "Headers": dict([(i, res.headers[i]) for i in res.headers]),
            "RequestId": res.request_id,
            "Etag": res.etag,
            "VersionId": res.versionid,
            "DeleteMarker": res.delete_marker,
        }

    def sign_url(self, req):
        req = merge(req, {
            "Method": "GET",
            "Key": REQUIRED,
            "Expires": 1800,
            "Headers": None,
            "Params": None,
            "SlashSafe": False,
        })
        res = self.client.sign_url(
            method=req["Method"],
            key=req["Key"],
            expires=req["Expires"],
            headers=req["Headers"],
            params=req["Params"],
            slash_safe=req["SlashSafe"],
        )
        return {
            "DownloadURL": res
        }

