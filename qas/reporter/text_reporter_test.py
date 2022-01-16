#!/usr/bin/env python3


import unittest
from .text_reporter import *


class TestTextReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.reporter = TextReporter

    def test_get_val_from_key(self):
        d = {
            "key1": [{
                "key2": "val0-2",
            }, {
                "key2": "val1-2",
            }]
        }
        self.reporter.append_val_to_key(d, "key1.1.key2", "set_vals")
        print(d)


if __name__ == "__main__":
    unittest.main()
