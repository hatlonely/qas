#!/usr/bin/env python3


import json
import unittest
import mns.mns_client
from mns.account import Account
from mns.topic import TopicMessage

from .mns_driver import MNSDriver

host = "http://xx.mns.cn-shanghai.aliyuncs.com"
access_key_id = "xx"
access_key_secret = "xx"
topic = "test-mns-topic-shanghai"
queue = "test-mns-queue-shanghai"


class TestMNSTopic(unittest.TestCase):
    def test_mns_client_public_message(self):
        client = mns.mns_client.MNSClient(
            host=host,
            access_id=access_key_id,
            access_key=access_key_secret,
        )

        req = mns.mns_client.PublishMessageRequest(
            topic_name=topic,
            message_body="hello world 123",
            message_tag="",
            direct_mail=None,
            direct_sms=None,
        )
        res = mns.mns_client.PublishMessageResponse()
        client.publish_message(req, res)
        print({
            "MessageId": res.message_id,
            "MessageBodyMD5": res.message_body_md5,
        })

    def test_mns_client_receive_message(self):
        client = mns.mns_client.MNSClient(
            host=host,
            access_id=access_key_id,
            access_key=access_key_secret,
        )

        req = mns.mns_client.ReceiveMessageRequest(
            queue_name=queue,
            base64decode=False,
            wait_seconds=1,
        )
        res = mns.mns_client.ReceiveMessageResponse()
        client.receive_message(req, res)
        res = {
            "MessageId": res.message_id,
            "ReceiptHandle": res.receipt_handle,
            "MessageBodyMD5": res.message_body_md5,
            "MessageBody": res.message_body,
            "EnqueueTime": res.enqueue_time,
            "NextVisibleTime": res.next_visible_time,
            "FirstDequeueTime": res.first_dequeue_time,
            "DequeueCount": res.dequeue_count,
            "Priority": res.priority,
            "Body": json.loads(res.message_body),
        }
        print(json.dumps(res, indent=True))

    def test_mns_topic(self):
        account = Account(
            host=host,
            access_id=access_key_id,
            access_key=access_key_secret,
        )
        client = account.get_topic(topic)
        # res = topic.publish_message(TopicMessage(base64.b64encode("hello world".encode("utf-8")).decode("utf-8")))
        res = client.publish_message(TopicMessage('hello world'))
        print(res.message_id)
        print({
            "MessageId": res.message_id,
            "MessageBodyMD5": res.message_body_md5,
        })

    # 这种方式会自动对 message body 进行 base64 解码，奇奇怪怪的，调试好久没调通，建议直接使用 mns_client 底层接口即可
    def test_mns_queue(self):
        account = Account(
            host=host,
            access_id=access_key_id,
            access_key=access_key_secret,
        )
        client = account.get_queue(queue)
        res = client.receive_message(1)
        res = {
            "MessageId": res.message_id,
            "ReceiptHandle": res.receipt_handle,
            "MessageBodyMD5": res.message_body_md5,
            "MessageBody": res.message_body,
            "EnqueueTime": res.enqueue_time,
            "NextVisibleTime": res.next_visible_time,
            "FirstDequeueTime": res.first_dequeue_time,
            "DequeueCount": res.dequeue_count,
            "Priority": res.priority,
        }
        print(res["MessageBody"])


class TestMNSDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = MNSDriver({
            "AccessKeyId": access_key_id,
            "AccessKeySecret": access_key_secret,
            "Endpoint": host,
        })

    def test_publish_message(self):
        res = self.driver.do({
            "Action": "PublishMessage",
            "Topic": topic,
            "MessageBody": "hello world 123",
            "Body": {},
        })
        print(json.dumps(res, indent=True))

    def test_publish_message_json(self):
        res = self.driver.do({
            "Action": "PublishMessage",
            "Topic": topic,
            "MessageBody": "",
            "Body": {
                "key1": "val1",
                "key2": "val2",
            },
        })
        print(json.dumps(res, indent=True))

    def test_receive_message(self):
        res = self.driver.do({
            "Action": "ReceiveMessage",
            "Queue": queue,
        })
        print(json.dumps(res, indent=True))


if __name__ == "__main__":
    unittest.main()
