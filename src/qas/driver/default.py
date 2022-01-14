#!/usr/bin/env python3


import unittest


def merge(req, dft):
    return _merge_recursive("", req, dft)


def _merge_recursive(root: str, req, dft):
    if isinstance(dft, dict):
        for key, val in dft.items():
            root_dot_key = "{}.{}".format(root, key).lstrip(".")
            if isinstance(val, dict):
                req[key] = _merge_recursive(root_dot_key, req[key] if key in req else {}, val)
            elif isinstance(val, list):
                req[key] = _merge_recursive(root_dot_key, req[key] if key in req else [], val)
            else:
                if val == "required" and key not in req:
                    raise Exception("missing required key [{}]".format(root_dot_key))
                elif key not in req:
                    req[key] = val
    if isinstance(dft, list):
        for idx, val in enumerate(dft):
            root_dot_key = "{}.{}".format(root, idx).lstrip(".")
            if isinstance(val, dict):
                while idx >= len(req):
                    req.append({})
                req[idx] = _merge_recursive(root_dot_key, req[idx], val)
            elif isinstance(val, list):
                while idx >= len(req):
                    req.append([])
                req[idx] = _merge_recursive(root_dot_key, req[idx], val)
            else:
                if val == "required" and idx >= len(req):
                    raise Exception("missing required key [{}]".format(root_dot_key))
                elif idx >= len(req):
                    req.append(val)
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
        with self.assertRaises(Exception) as cm:
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
        self.assertTrue("missing required key [key2.key4]" in str(cm.exception))

    def test_merge_ots_create_table(self):
        dft = {
            "TableMeta": {
                "TableName": "required",
                "SchemeEntry": [["required", "required"]]
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
