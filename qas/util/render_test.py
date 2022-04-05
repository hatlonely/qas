#!/usr/bin/env python3


import unittest
import json
from .render import render


def func(**kwargs):
    print(kwargs)
    for k in kwargs:
        print(k, "=>", kwargs[k])
    env = locals()
    env.update(**kwargs)
    print(eval("a + b"))


class TestKwArgs(unittest.TestCase):
    def test_kwargs(self):
        func(a="hello", b="world")


class TestRender(unittest.TestCase):
    def test_render(self):
        res = render({
            "key1": "val1",
            "#key2": "case['key2']",
            "key3": [{
                "key4": "val4",
                "#key5": "case['key5']"
            }],
            "$key6": "echo -n 'val6'",
        }, case={
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
            }],
            "key6": "val6"
        })


if __name__ == '__main__':
    unittest.main()

