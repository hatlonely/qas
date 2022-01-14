#!/usr/bin/env python3

import unittest


def merge(req, dft):
    return _merge_recursive("", req, dft)


def _merge_recursive(root: str, req, dft):
    if isinstance(dft, dict):
        to_enumerate = dft.items()
    else:
        to_enumerate = enumerate(dft)

    for key, val in to_enumerate:
        root_dot_key = "{}.{}".format(root, key).lstrip(".")
        if isinstance(val, dict):
            req[key] = _merge_recursive(root_dot_key, req[key], val)
        elif isinstance(val, list):
            req[key] = _merge_recursive(root_dot_key, req[key], val)
        else:
            if val == "required" and key not in req:
                raise Exception("missing required key [{}]".format(root_dot_key))
            elif key not in req:
                req[key] = val
    return req


class TestExpectVal(unittest.TestCase):
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
        with self.assertRaises(Exception) as context:
            merge({
                "key1": "val1",
                "key2": {
                    "key3": "val3"
                }
            }, {
                "key1": "required",
                "key2": {
                    "key4": "required",
                }
            })
            self.assertTrue("missing required key [key2.key4]" in context.exception)


if __name__ == '__main__':
    unittest.main()
