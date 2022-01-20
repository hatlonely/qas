#!/usr/bin/env python3


import json
import unittest
import oss2

from .oss_driver import OSSDriver


access_key_id = "xx"
access_key_secret = "xx"
endpoint = "http://oss-cn-shanghai.aliyuncs.com"
bucket = "xx"


class TestOSS(unittest.TestCase):
    def setUp(self) -> None:
        self.client = oss2.Bucket(
            oss2.Auth(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
            ),
            endpoint=endpoint,
            bucket_name=bucket,
        )

    def test_get_object_meta(self):
        res = self.client.get_object_meta(key="test-file.txt")
        res = {
            "Status": res.status,
            "Headers": dict([(i, res.headers[i]) for i in res.headers]),
            "RequestId": res.request_id,
            "Etag": res.etag,
            "ContentLength": res.content_length,
            "LastModified": res.last_modified,
            "VersionId": res.versionid,
            "DeleteMarker": res.delete_marker,
        }
        print(json.dumps(res, indent=True))

    def test_sign_url(self):
        res = self.client.sign_url(
            method="GET",
            key="test-file.txt",
            expires=1800,
            headers=None,
            params=None,
        )
        print(res)

    def test_get_object_to_file(self):
        res = self.client.get_object_to_file("test-file.txt", "test-file.txt")
        res = {
            "Status": res.status,
            "Headers": dict([(i, res.headers[i]) for i in res.headers]),
            "RequestId": res.request_id,
            "Etag": res.etag,
            "ContentLength": res.content_length,
            "LastModified": res.last_modified,
            "VersionId": res.versionid,
            "DeleteMarker": res.delete_marker,
        }
        print(json.dumps(res, indent=True))

    def test_put_object_from_file(self):
        res = self.client.put_object_from_file("test-file.txt", "test-file.txt")
        res = {
            "Status": res.status,
            "Headers": dict([(i, res.headers[i]) for i in res.headers]),
            "RequestId": res.request_id,
            "Etag": res.etag,
            "VersionId": res.versionid,
            "DeleteMarker": res.delete_marker,
        }
        print(json.dumps(res, indent=True))


class TestOSSDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = OSSDriver({
            "AccessKeyId": access_key_id,
            "AccessKeySecret": access_key_secret,
            "Endpoint": endpoint,
            "Bucket": bucket,
        })

    def test_get_object_meta(self):
        res = self.driver.do({
            "Action": "GetObjectMeta",
            "Key": "test-file.txt"
        })
        print(json.dumps(res, indent=True))

    def test_sign_url(self):
        res = self.driver.do({
            "Action": "SignURL",
            "Key": "test-file.txt"
        })
        print(json.dumps(res))

    def test_get_object_to_file(self):
        res = self.driver.do({
            "Action": "GetObjectToFile",
            "Key": "test-file.txt",
            "Filename": "test-file.txt"
        })
        print(json.dumps(res, indent=True))

    def test_put_object_from_file(self):
        res = self.driver.do({
            "Action": "PutObjectFromFile",
            "Key": "test-file.txt",
            "Filename": "test-file.txt"
        })
        print(json.dumps(res, indent=True))


if __name__ == "__main__":
    pass
