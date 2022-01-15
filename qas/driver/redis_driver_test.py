#!/usr/bin/env python3

import unittest
import redis


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
        self.client.set("name", "hatlonely123")

    def test_get(self):
        res = self.client.get("name")
        print(res)


if __name__ == '__main__':
    unittest.main()


