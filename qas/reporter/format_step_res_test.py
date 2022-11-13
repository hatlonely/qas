#!/usr/bin/env python3

import unittest
from .format_step_res import escape_html


class TestEscapeHtml(unittest.TestCase):
    def test_escape(self):
        res = escape_html({
            "key1": "oss://<bucket>/<object>",
            "key2": ["<bucket>", "<object>", 1, "hello"]
        })
        print(res)
        self.assertDictEqual(res, {
            "key1": "oss://&lt;bucket&gt;/&lt;object&gt;",
            "key2": ["&lt;bucket&gt;", "&lt;object&gt;", 1, "hello"]
        })
