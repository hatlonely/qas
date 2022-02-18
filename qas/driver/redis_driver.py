#!/usr/bin/env python3


import json
import redis

from ..util import merge, REQUIRED
from .driver import Driver


class RedisDriver(Driver):
    client: redis.Redis

    def __init__(self, args):
        args = merge(args, {
            "host": 'localhost',
            "port": 6379,
            "db": 0,
            "password": None,
        })
        self.client = redis.Redis(
            host=args["host"],
            port=args["port"],
            db=args["db"],
            password=args["password"],
            decode_responses=True,
        )

    def name(self, req):
        return req["cmd"]

    def do(self, req):
        req = merge(req, {
            "cmd": REQUIRED,
        })

        do_map = {
            "set": self.set,
            "get": self.get,
            "setJson": self.set_json,
            "getJson": self.get_json,
            "hset": self.hset,
            "hget": self.hget,
            "del": self.delete,
            "hdel": self.hdel,
        }

        if req["cmd"] not in do_map:
            raise Exception("unsupported cmd [{}]".format(req["cmd"]))

        return do_map[req["cmd"]](req)

    def set(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "val": REQUIRED,
            "exp": None,
        })
        ok = self.client.set(req["key"], req["val"], ex=req["exp"])
        return {"ok": ok}

    def get(self, req):
        req = merge(req, {
            "key": REQUIRED
        })
        val = self.client.get(req["key"])
        return {"val": val}

    def delete(self, req):
        req = merge(req, {
            "key": REQUIRED,
        })
        ok = self.client.delete(req["key"])
        return {"ok": ok}

    def set_json(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "val": REQUIRED,
            "exp": None,
        })
        ok = self.client.set(req["key"], json.dumps(req["val"]), ex=req["exp"])
        return {"ok": ok}

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
        return {"n": n}

    def hget(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "field": REQUIRED,
        })
        val = self.client.hget(req["key"], req["field"])
        return {"val": val}

    def hdel(self, req):
        req = merge(req, {
            "key": REQUIRED,
            "field": REQUIRED,
        })
        n = self.client.hdel(req["key"], req["field"])
        return {"n": n}
