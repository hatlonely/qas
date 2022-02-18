#!/usr/bin/env python3


import json
import mns.mns_client
import mns.mns_exception
from ..util import merge, REQUIRED
from .driver import Driver


class MNSDriver(Driver):
    client: mns.mns_client.MNSClient

    def __init__(self, args):
        args = merge(args, {
            "AccessKeyId": REQUIRED,
            "AccessKeySecret": REQUIRED,
            "Endpoint": REQUIRED,
        })
        self.client = mns.mns_client.MNSClient(
            host=args["Endpoint"],
            access_id=args["AccessKeyId"],
            access_key=args["AccessKeySecret"],
        )

    def name(self, req):
        return req["Action"]

    def do(self, req):
        req = merge(req, {
            "Action": REQUIRED
        })

        do_map = {
            "PublishMessage": self.publish_message,
            "ReceiveMessage": self.receive_message,
            "DeleteMessage": self.delete_message,
        }
        if req["Action"] not in do_map:
            raise Exception("unsupported action [{}]".format(req["Action"]))

        try:
            return do_map[req["Action"]](req)
        except mns.mns_exception.MNSServerException as e:
            return {
                "Type": e.type,
                "Message": e.message,
                "HostId": e.host_id,
                "RequestId": e.request_id,
            }
        except Exception as e:
            raise e

    def publish_message(self, req):
        req = merge(req, {
            "Topic": REQUIRED,
            "MessageBody": "",
            "Body": {},
            "MessageTag": "",
            "DirectMail": None,
            "DirectSms": None,
        })

        req = mns.mns_client.PublishMessageRequest(
            topic_name=req["Topic"],
            message_body=req["MessageBody"] if req["MessageBody"] else json.dumps(req["Body"]),
            message_tag=req["MessageTag"],
            direct_mail=req["DirectMail"],
            direct_sms=req["DirectSms"],
        )
        res = mns.mns_client.PublishMessageResponse()
        self.client.publish_message(req, res)

        return {
            "Status": res.status,
            "Header": res.header,
            "RequestId": res.get_requestid(),
            "MessageId": res.message_id,
            "MessageBodyMD5": res.message_body_md5,
        }

    def receive_message(self, req):
        req = merge(req, {
            "Queue": REQUIRED,
            "Base64Decode": False,
            "WaitSeconds": -1,
            "AutoRelease": True,
        })

        receive_message_req = mns.mns_client.ReceiveMessageRequest(
            queue_name=req["Queue"],
            base64decode=req["Base64Decode"],
            wait_seconds=req["WaitSeconds"],
        )
        receive_message_res = mns.mns_client.ReceiveMessageResponse()

        self.client.receive_message(receive_message_req, receive_message_res)

        body = None
        try:
            body = json.loads(receive_message_res.message_body)
            body["Body"] = json.loads(body["Message"])
        except json.decoder.JSONDecodeError as e:
            pass
        except Exception as e:
            raise e

        if req["AutoRelease"]:
            delete_message_req = mns.mns_client.DeleteMessageRequest(
                queue_name=req["Queue"],
                receipt_handle=receive_message_res.receipt_handle,
            )
            delete_message_res = mns.mns_client.DeleteMessageResponse()
            self.client.delete_message(delete_message_req, delete_message_res)

        return {
            "Status": receive_message_res.status,
            "Header": receive_message_res.header,
            "RequestId": receive_message_res.get_requestid(),
            "MessageId": receive_message_res.message_id,
            "ReceiptHandle": receive_message_res.receipt_handle,
            "MessageBodyMD5": receive_message_res.message_body_md5,
            "MessageBody": receive_message_res.message_body,
            "EnqueueTime": receive_message_res.enqueue_time,
            "NextVisibleTime": receive_message_res.next_visible_time,
            "FirstDequeueTime": receive_message_res.first_dequeue_time,
            "DequeueCount": receive_message_res.dequeue_count,
            "Priority": receive_message_res.priority,
            "Body": body,
        }

    def delete_message(self, req):
        req = merge(req, {
            "Queue": REQUIRED,
            "ReceiptHandle": REQUIRED,
        })

        req = mns.mns_client.DeleteMessageRequest(
            queue_name=req["Queue"],
            receipt_handle=req["ReceiptHandle"]
        )
        res = mns.mns_client.DeleteMessageResponse()

        try:
            self.client.delete_message(req, res)
        except Exception as e:
            raise e

        return {
            "Status": res.status,
            "Header": res.header,
            "RequestId": res.get_requestid(),
        }
