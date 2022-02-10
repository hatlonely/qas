#!/usr/bin/env python3


import unittest
import json
from .render import render


class TestRender(unittest.TestCase):
    def test_render(self):
        res = render({
            "key1": "val1",
            "#key2": "case['key2']",
            "key3": [{
                "key4": "val4",
                "#key5": "case['key5']"
            }],
        }, {
            "key2": 2,
            "key5": "val5"
        })
        print(json.dumps(res, indent=True))
        self.assertDictEqual(res, {
          "key1": "val1",
          "key2": 2,
          "key3": [{
             "key4": "val4",
             "key5": "val5"
           }]
        })


if __name__ == '__main__':
    unittest.main()

