#!/usr/bin/env python3


def expect_map(root, vals, rules):
    for key in rules:
        rule = rules[key]
        val = vals[key]
        root_dot_key = "{}.{}".format(root, key).lstrip(".")
        if isinstance(rule, dict):
            node, msg, ok = expect_map(root_dot_key, val, rule)
            if not ok:
                return node, msg, False
        else:
            if key.startswith("$"):
                msg, ok = expect_val(root_dot_key, val, rule)
                if not ok:
                    return root_dot_key, msg, False
            else:
                if val != rule:
                    return root_dot_key, "val not equal. val: [{}], expect: [{}]".format(rule, val), False
    return "", "", True


def expect_val(root, val, rule):
    return True
