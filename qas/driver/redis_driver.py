#!/usr/bin/env python3


import json
import redis
from .default import merge, REQUIRED


class RedisDriver:
    client: redis.Redis

    def __init__(self, args):
        args = merge(args, {
            "host": 'localhost',
            "port": 6379,
            "db": 0,
            "password": None,
        })
        self.client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            decode_responses=True,
        )

    def do(self, req):
        req = merge(req, {
            "cmd": REQUIRED,
        })

        do_map = {
            "set": self.set,
            "get": self.get,
            "setJson": self.set_json,
            "getJson": self.get_json,
        }

        if req["cmd"] not in do_map:
            raise Exception("unsupported cmd [{}]".format(req["cmd"]))

        return do_map[req["cmd"]](req)

    def set(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "val": REQUIRED,
            "expiration": None,
        })
        ok = self.client.set(req["key"], req["val"], ex=req["expiration"])
        return {
            "ok": ok
        }

    def get(self, req):
        req = merge(req, {
            "key": REQUIRED
        })
        val = self.client.get(req["key"])
        return {
            "val": val
        }

    def set_json(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "val": REQUIRED,
            "expiration": None,
        })
        ok = self.client.set(req["key"], json.dumps(req["val"]), ex=req["expiration"])
        return {
            "ok": ok
        }

    def get_json(self, req):
        req = merge(req, {
            "key": REQUIRED
        })
        res = self.client.get(req["key"])
        return json.loads(res)

    def hset(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "field": REQUIRED,
            "val": REQUIRED,
        })
        n = self.client.hset(req["key"], req["field"], req["val"])
        return {
            "n": n
        }

    def hget(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "field": REQUIRED,
        })
        val = self.client.hget(req["key"], req["field"])
        return {
            "val": val
        }