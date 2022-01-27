#!/usr/bin/env python3


import itertools
import json
import unittest
import os


class TestTravel(unittest.TestCase):
    def test_travel(self):
        print([i for i in os.listdir("..") if os.path.isdir(os.path.join("..", i))])


class TestForLoop(unittest.TestCase):
    def test_for_loop(self):
        for i in range(1):
            print("body")
            break
        else:
            print("else")


def generate(d):
    if isinstance(d, list):
        return itertools.product(*[generate(val) for val in d])
    if isinstance(d, dict):
        return [
            dict(i)
            for i in itertools.product(*[
                [
                    (kv[0][1:], i) for i in kv[1]
                ]
                if kv[0].startswith("!") else
                [
                    *[(kv[0], i) for i in generate(kv[1])]
                ]
                for kv in d.items()
            ])
        ]
    return d,


class TestGenerate(unittest.TestCase):
    def test_generate(self):
        count = 0
        for req in generate({
            "!key1": [1, 2],
            "key2": {
                "!key3": [3, 4],
            },
            "key4": [{
                "!key5": [5, 6],
            }, {
                "key6": "val6",
                "!key7": [7, 8, 9],
            }]
        }):
            count += 1
            print(count, json.dumps(req))


if __name__ == '__main__':
    unittest.main()

