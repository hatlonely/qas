#!/usr/bin/env python3


import unittest
from .generate import generate_res, generate_req, calculate_num, grouper


class TestGenerate(unittest.TestCase):
    def test_calculate_num(self):
        self.assertEqual(calculate_num({
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
        }), 24)

    def test_generate_res(self):
        res = list(generate_res({
            "!key1": [1, 2],
            "key2": {
                "!key3": [3, 4],
            },
            "key4": [{
                "!key5": [5, 6],
            }, {
                "key6": "val6",
                "!key7": [7, 8],
            }],
        }, 2))
        self.assertListEqual(res, [
            {'key1': 1, 'key2': {'key3': 3}, 'key4': ({'key5': 5}, {'key6': 'val6', 'key7': 7})},
            {'key1': 2, 'key2': {'key3': 4}, 'key4': ({'key5': 6}, {'key6': 'val6', 'key7': 8})},
        ])

    def test_generate_req(self):
        res = list(generate_req({
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
        }))
        self.assertListEqual(res, [
            {"key1": 1, "key2": {"key3": 3}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 7})},
            {"key1": 1, "key2": {"key3": 3}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 8})},
            {"key1": 1, "key2": {"key3": 3}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 9})},
            {"key1": 1, "key2": {"key3": 3}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 7})},
            {"key1": 1, "key2": {"key3": 3}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 8})},
            {"key1": 1, "key2": {"key3": 3}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 9})},
            {"key1": 1, "key2": {"key3": 4}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 7})},
            {"key1": 1, "key2": {"key3": 4}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 8})},
            {"key1": 1, "key2": {"key3": 4}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 9})},
            {"key1": 1, "key2": {"key3": 4}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 7})},
            {"key1": 1, "key2": {"key3": 4}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 8})},
            {"key1": 1, "key2": {"key3": 4}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 9})},
            {"key1": 2, "key2": {"key3": 3}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 7})},
            {"key1": 2, "key2": {"key3": 3}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 8})},
            {"key1": 2, "key2": {"key3": 3}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 9})},
            {"key1": 2, "key2": {"key3": 3}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 7})},
            {"key1": 2, "key2": {"key3": 3}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 8})},
            {"key1": 2, "key2": {"key3": 3}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 9})},
            {"key1": 2, "key2": {"key3": 4}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 7})},
            {"key1": 2, "key2": {"key3": 4}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 8})},
            {"key1": 2, "key2": {"key3": 4}, "key4": ({"key5": 5}, {"key6": "val6", "key7": 9})},
            {"key1": 2, "key2": {"key3": 4}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 7})},
            {"key1": 2, "key2": {"key3": 4}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 8})},
            {"key1": 2, "key2": {"key3": 4}, "key4": ({"key5": 6}, {"key6": "val6", "key7": 9})},
        ])

    def test_grouper(self):
        res = list(grouper([1, 2, 3, 4, 5, 6, 7], 3))
        self.assertListEqual(res, [
            [1, 2, 3],
            [4, 5, 6],
            [7],
        ])

        res = list(grouper([1, 2, 3, 4, 5, 6, 7], 0))
        self.assertListEqual(res, [
            [1, 2, 3, 4, 5, 6, 7]
        ])


if __name__ == '__main__':
    unittest.main()
