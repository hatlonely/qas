#!/usr/bin/env python3

import unittest
import redis
from .redis_driver import *


# https://github.com/redis/redis-py
class TestRedis(unittest.TestCase):
    def setUp(self) -> None:
        self.client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            decode_responses=True,
        )

    def test_set(self):
        ok = self.client.set("name", "hatlonely123")
        print(ok)

    def test_get(self):
        res = self.client.get("name")
        print(res)

    def test_hset(self):
        num = self.client.hset("key", "f1", "v1")
        print(num)

    def test_hget(self):
        res = self.client.hget("key", "f1")
        print(res)


class TestRedisDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = RedisDriver(args={})

    def test_set(self):
        res = self.driver.do(req={
            "cmd": "set",
            "key": "key1",
            "val": "val1",
            "exp": 60,
        })
        print(res)

    def test_get(self):
        res = self.driver.do(req={
            "cmd": "get",
            "key": "key1"
        })
        print(res)

    def test_set_json(self):
        res = self.driver.do(req={
            "cmd": "setJson",
            "key": "key1",
            "val": {
                "key1": "val1",
                "key2": "val2",
                "key3": 3,
            }
        })
        print(res)

    def test_get_json(self):
        res = self.driver.do(req={
            "cmd": "getJson",
            "key": "key1",
        })
        print(res)


if __name__ == '__main__':
    unittest.main()


