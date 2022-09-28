#!/usr/bin/env python3

import json
import unittest

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from .cos_driver import COSDriver


secret_id = "xx"
secret_key = "xx"
bucket = "xx"
region = "ap-beijing"


class TestCOS(unittest.TestCase):
    def setUp(self) -> None:
        self.client = CosS3Client(CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Token=None,
            Scheme="https",
        ))

    def test_upload_file(self):
        res = self.client.upload_file(
            Bucket=bucket,
            Key='hl/oss_driver.py',
            LocalFilePath='oss_driver.py',
            EnableMD5=False,
            progress_callback=None
        )
        print(type(res))
        print(json.dumps(res, indent=2))


class TestCOSDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = COSDriver({
            "SecretId": secret_id,
            "SecretKey": secret_key,
            "Region": region,
            "Bucket": bucket,
        })

    def test_upload_file(self):
        res = self.driver.do({
            "Action": "UploadFile",
            "Key": "hl/oss_driver.py",
            "LocalFilePath": "oss_driver.py",
            "EnableMD5": False,
        })
        print(json.dumps(res, indent=2))
