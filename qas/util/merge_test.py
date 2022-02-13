#!/usr/bin/env python3


import unittest
from .merge import *


class TestMerge(unittest.TestCase):
    def test_merge_dict(self):
        req = merge({
            "key1": "val1",
            "key2": {
                "key3": "val3",
            },
            "key6": [{
                "key7": "val7",
            }, {
                "key8": "val8",
            }]
        }, {
            "key2": {
                "key3": "dftVal3",
                "key4": "dftVal4",
            },
            "key5": "dftVal5",
            "key6": [{
                "key7": "dftVal7",
                "key8": "dftVal8",
            }, {
                "key7": "dftVal7",
                "key8": "dftVal8",
            }]
        })

        self.assertDictEqual(req, {
            "key1": "val1",
            "key2": {
                "key3": "val3",
                "key4": "dftVal4"
            },
            "key5": "dftVal5",
            "key6": [{
                "key7": "val7",
                "key8": "dftVal8",
            }, {
                "key7": "dftVal7",
                "key8": "val8",
            }]
        })

    def test_merge_list(self):
        req = merge([{
            "key7": "val7",
        }, {
            "key8": "val8",
        }], [{
            "key7": "dftVal7",
            "key8": "dftVal8",
        }, {
            "key7": "dftVal7",
            "key8": "dftVal8",
        }])
        self.assertListEqual(req, [{
            "key7": "val7",
            "key8": "dftVal8",
        }, {
            "key7": "dftVal7",
            "key8": "val8",
        }])

    def test_merge_required(self):
        with self.assertRaises(Exception) as cm:
            merge({
                "key1": "val1",
                "key2": {
                    "key3": "val3"
                }
            }, {
                "key1": REQUIRED,
                "key2": {
                    "key4": REQUIRED,
                }
            })
        self.assertTrue("missing required key [key2.key4]" in str(cm.exception))

    def test_merge_ots_create_table(self):
        dft = {
            "TableMeta": {
                "TableName": REQUIRED,
                "SchemeEntry": [[REQUIRED, REQUIRED]]
            },
            "TableOptions": {
                "TimeToLive": -1,
                "MaxVersion": 1,
                "MaxTimeDeviation": 86400,
            }
        }

        with self.assertRaises(Exception) as cm:
            merge({}, dft)
        self.assertTrue("missing required key [TableMeta.TableName]" in str(cm.exception))

        with self.assertRaises(Exception) as cm:
            merge({
                "TableMeta": {
                    "TableName": "test-table",
                },
            }, dft)
        self.assertTrue("missing required key [TableMeta.SchemeEntry.0.0]" in str(cm.exception))

        with self.assertRaises(Exception) as cm:
            merge({
                "TableMeta": {
                    "TableName": "test-table",
                    "SchemeEntry": [
                        ["key"]
                    ]
                },
            }, dft)
        self.assertTrue("missing required key [TableMeta.SchemeEntry.0.1]" in str(cm.exception))


if __name__ == '__main__':
    unittest.main()

