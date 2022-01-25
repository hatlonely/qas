#!/usr/bin/env python3


import json
import unittest

import bson.json_util
import pymongo
from bson.objectid import ObjectId

from .mongo_driver import MongoDriver, flat


class TestMongo(unittest.TestCase):
    def setUp(self) -> None:
        self.client = pymongo.MongoClient(
            host="localhost",
            port=27017,
        )
        self.database = self.client.get_database("some_database")
        self.collection = self.database.get_collection("some_collection")

    def test_count_documents(self):
        db = self.client.some_database
        col = db["some_collection"]
        total_docs = col.count_documents({})
        print(total_docs)

    def test_count_documents2(self):
        db = self.client.get_database("some_database")
        col = db.get_collection("some_collection")
        total_docs = col.count_documents({})
        print(total_docs)

    def test_insert_documents(self):
        # res = self.collection.insert_one({
        #   "key1": "value1",
        #   "key2": "value2",
        #   "key3": {
        #     "key4": "value5",
        #     "key5": 5,
        #     "key6": [
        #       "value61",
        #       "value62"
        #     ],
        #     "key7": [
        #       {
        #         "key8": "value8"
        #       }
        #     ]
        #   }
        # })

        res = self.collection.update_one({"_id": ObjectId("61ef739496089fa658380996")}, {
            "$set": {
                "key1": "value1",
                "key2": "value2",
                "key3": {
                    "key4": "value5",
                    "key5": 5,
                    "key6": [
                        "value61",
                        "value62"
                    ],
                    "key7": [
                        {
                            "key8": "value8"
                        }
                    ]
                }
            }
        })
        print(res)

    def test_get_documents(self):
        res = self.collection.find_one(ObjectId("61ef739496089fa658380996"))
        print(res)
        print(dict(res))
        print(json.dumps(dict(res), default=lambda x: str(x)))
        print(bson.json_util.dumps(res))

    def test_update_documents(self):
        res = self.collection.update_one({"_id": ObjectId("61ef739496089fa658380996")}, {"$set": {"key2": "val2"}}, upsert=True)
        print(res)
        print(res.matched_count, res.modified_count, res.acknowledged, res.upserted_id)


class TestMongoDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = MongoDriver({
            "host": "localhost",
            "port": 27017,
            "database": "some_database"
        })

    def test_insert_one(self):
        res = self.driver.do({
            "cmd": "insertOne",
            "collection": "some_collection",
            "document": {
              "key1": "value1",
              "key2": "value2",
              "key3": {
                "key4": "value5",
                "key5": 5,
                "key6": [
                  "value61",
                  "value62"
                ],
                "key7": [
                  {
                    "key8": "value8"
                  }
                ]
              }
            }
        })
        print(json.dumps(res))

    def test_find_one(self):
        res = self.driver.do({
            "cmd": "findOne",
            "collection": "some_collection",
            "_id": "61ef858608289cdcca960b89",
        })
        print(json.dumps(res, indent=2))

    def test_update_one(self):
        res = self.driver.do({
            "cmd": "updateOne",
            "collection": "some_collection",
            "_id": "61ef858608289cdcca960b89",
            "update": {
                "key3": {
                    "key4": "val55",
                }
            }
        })
        print(json.dumps(res))


class TestFlat(unittest.TestCase):
    def test_flat(self):
        d = flat({
          "key1": "value1",
          "key2": "value2",
          "key3": {
            "key4": "value5",
            "key5": 5,
            "key6": [
              "value61",
              "value62"
            ],
            "key7": [
              {
                "key8": "value8"
              }
            ]
          }
        })
        print(json.dumps(d, indent=2))


if __name__ == "__main__":
    unittest.main()
