#!/usr/bin/env python3


from elasticsearch import Elasticsearch
from datetime import datetime

from .driver import Driver
from ..util import merge, REQUIRED


class ElasticSearchDriver(Driver):
    def __init__(self, args):
        args = merge(args, {
            "endpoint": "http://localhost:9200",
            "username": "",
            "password": "",
        })

        if args["username"]:
            self.client = Elasticsearch(
                args["endpoint"].split(","),
                http_auth=(args["username"], args["password"])
            )
        else:
            self.client = Elasticsearch(
                args["endpoint"].split(","),
            )

    def name(self, req):
        return req["cmd"]

    def do(self, req):
        req = merge(req, {
            "cmd": REQUIRED,
        })

        do_map = {
            "index": self.index,
            "get": self.get,
            "search": self.search,
            "delete": self.delete,
        }

        if req["cmd"] not in do_map:
            raise Exception("unsupported cmd [{}]".format(req["cmd"]))

        return do_map[req["cmd"]](req)

    def index(self, req):
        req = merge(req, {
            "index": REQUIRED,
            "id": REQUIRED,
            "document": REQUIRED,
        })
        return self.client.index(index=req["index"], id=req["id"], document=req["document"])

    def get(self, req):
        req = merge(req, {
            "index": REQUIRED,
            "id": REQUIRED,
        })
        return self.client.get(index=req["index"], id=req["id"])

    def search(self, req):
        req = merge(req, {
            "index": REQUIRED,
            "query": {
                "match_all": {}
            }
        })

        return self.client.search(index=req["index"], query=req["query"])

    def delete(self, req):
        req = merge(req, {
            "index": REQUIRED,
            "id": REQUIRED,
        })
        return self.client.delete(index=req["index"], id=req["id"])
