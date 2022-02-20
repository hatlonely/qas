#!/usr/bin/env python3


import unittest
import requests

from .dingtalk_hook import *


class TestDingTalk(unittest.TestCase):
    def test_ding_talk(self):
        endpoint = "https://oapi.dingtalk.com/robot/send"
        access_token = "xxx"
        secret = "xxx"

        ts, sign = calculate_sign(secret)

        res = requests.post(
            url="https://oapi.dingtalk.com/robot/send",
            params={
                "access_token": access_token,
                "timestamp": ts,
                "sign": sign,
            },
            headers={
                "Content-Type": "application/json"
            },
            # json={
            #     "msgtype": "text",
            #     "text": {
            #         "content": "我就是我, 是不一样的烟火",
            #     }
            # },
            json={
                "msgtype": "actionCard",
                "actionCard": {
                    "title": "我 20 年前想打造一间苹果咖啡厅，而它正是 Apple Store 的前身",
                    "text": "![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png) \n\n #### 乔布斯 20 年前想打造的苹果咖啡厅 \n\n Apple Store 的设计正从原来满满的科技感走向生活化，而其生活化的走向其实可以追溯到 20 年前苹果一个建立咖啡馆的计划",
                    "btnOrientation": "0",
                    "btns": [
                        {
                            "title": "内容不错",
                            "actionURL": "https://www.dingtalk.com/"
                        },
                        {
                            "title": "不感兴趣",
                            "actionURL": "https://www.dingtalk.com/"
                        }
                    ]
                }
            }
        )
        print(res.status_code)
        print(res.text)

    def test_calculate_sign(self):
        ts, sign = calculate_sign("hello world")
        print(ts, sign)


class TestDingTalkHook(unittest.TestCase):
    def test_ding_talk(self):
        hook = DingTalkHook({
            "accessToken": "xxx",
            "secret": "xxx",
        })

        res = TestResult("", "", "")
        res.status = "pass"

        hook.on_exit(res)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
