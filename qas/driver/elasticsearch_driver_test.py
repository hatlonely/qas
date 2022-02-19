#!/usr/bin/env python3


import unittest
from elasticsearch import Elasticsearch
from datetime import datetime

from .elasticsearch_driver import ElasticSearchDriver


class TestElasticSearch(unittest.TestCase):
    def test_elasticsearch(self):
        es = Elasticsearch(
            ["http://localhost:9200"],
        )

        res = es.index(index="test-index", id="123", document={
            "author": "kimchy",
            "text": "Elasticsearch: cool. bonsai cool.",
            "timestamp": datetime.now(),
        })
        print(res)

        res = es.get(index="test-index", id="123")
        print(res)

        res = es.search(index="test-index", query={"match_all": {}})
        print(res)

        res = es.delete(index="test-index", id="123")
        print(res)


class TestElasticSearchDriver(unittest.TestCase):
    def test_elasticsearch(self):
        driver = ElasticSearchDriver({
            "endpoint": "http://localhost:9200",
        })

        res = driver.do({
            "cmd": "index",
            "index": "test-index",
            "id": "123",
            "document": {
                "author": "kimchy",
                "text": "Elasticsearch: cool. bonsai cool.",
                "timestamp": datetime.now(),
            }
        })
        print(res)

        res = driver.do({
            "cmd": "get",
            "index": "test-index",
            "id": "123",
        })
        print(res)

        res = driver.do({
            "cmd": "search",
            "index": "test-index",
            "query": {
                "match_all": {}
            }
        })
        print(res)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
