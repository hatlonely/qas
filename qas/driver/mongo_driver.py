#!/usr/bin/env python3


import json
import pymongo
from bson.objectid import ObjectId

from ..util import merge, REQUIRED
from .driver import Driver


class MongoDriver(Driver):
    def __init__(self, args):
        args = merge(args, {
            "host": "localhost",
            "port": 27017,
            "database": REQUIRED,
        })

        self.client = pymongo.MongoClient(
            host=args["host"],
            port=args["port"],
        )
        self.database = self.client.get_database(args["database"])

    def name(self, req):
        return req["cmd"]

    def do(self, req):
        req = merge(req, {
            "cmd": REQUIRED
        })

        do_map = {
            "insertOne": self.insert_one,
            "findOne": self.find_one,
            "updateOne": self.update_one,
            "deleteOne": self.delete_one,
        }
        if req["cmd"] not in do_map:
            raise Exception("unsupported action [{}]".format(req["cmd"]))

        try:
            return do_map[req["cmd"]](req)
        except Exception as e:
            raise e

    def insert_one(self, req):
        req = merge(req, {
            "collection": REQUIRED,
            "document": REQUIRED,
        })
        collection = self.database.get_collection(req["collection"])
        res = collection.insert_one(req["document"])
        return {"_id": str(res.inserted_id)}

    def find_one(self, req):
        req = merge(req, {
            "collection": REQUIRED,
            "filter": {},
            "_id": "",
        })
        collection = self.database.get_collection(req["collection"])
        if req["_id"]:
            filter_ = {"_id": ObjectId(req["_id"])}
        else:
            filter_ = req["filter"]
        res = collection.find_one(filter_)
        return json.loads(json.dumps(dict(res), default=lambda x: str(x)))

    def update_one(self, req):
        req = merge(req, {
            "collection": REQUIRED,
            "filter": {},
            "_id": "",
            "update": {},
            "upsert": False,
        })
        collection = self.database.get_collection(req["collection"])
        if req["_id"]:
            filter_ = {"_id": ObjectId(req["_id"])}
        else:
            filter_ = req["filter"]

        res = collection.update_one(filter_, {"$set": flat(req["update"])}, upsert=req["upsert"])

        return {
            "acknowledged": res.acknowledged,
            "matchedCount": res.matched_count,
            "modifiedCount": res.modified_count,
        }

    def delete_one(self, req):
        req = merge(req, {
            "collection": REQUIRED,
            "filter": {},
            "_id": "",
        })
        collection = self.database.get_collection(req["collection"])
        if req["_id"]:
            filter_ = {"_id": ObjectId(req["_id"])}
        else:
            filter_ = req["filter"]
        res = collection.delete_one(filter_)
        return {
            "acknowledged": res.acknowledged,
            "deleteCount": res.deleted_count,
        }


def flat(d):
    res = {}
    _flat_recursive([], d, res)
    return res


def _flat_recursive(k, d, res):
    for key in d:
        if isinstance(d[key], dict):
            _flat_recursive(k + [key], d[key], res)
        else:
            res[".".join(k + [key])] = d[key]
