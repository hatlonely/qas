#!/usr/bin/env python3


import itertools
import functools


def generate_req(d, p="!"):
    if isinstance(d, list):
        return itertools.product(*[generate_req(v) for v in d])
    if isinstance(d, dict):
        return [
            dict(i)
            for i in itertools.product(*[
                [
                    (k[1:], i) for i in v
                ]
                if k.startswith(p) else
                [
                    *[(k, i) for i in generate_req(v)]
                ]
                for k, v in sorted(d.items())
            ])
        ]
    return d,


def generate_res(d, n, p="!"):
    if not d:
        return itertools.repeat(d, n)
    if isinstance(d, list):
        return zip(*[generate_res(v, n) for v in d])
    if isinstance(d, dict):
        return [
            dict(i)
            for i in zip(*[
                [(k[1:], i) for i in v]
                if k.startswith(p) else
                [(k, i) for i in generate_res(v, n)]
                for k, v in sorted(d.items())
            ])
        ]
    return itertools.repeat(d, n)


def calculate_num(d, p="!"):
    if isinstance(d, list):
        return functools.reduce(lambda x, y: x * y, [calculate_num(v) for v in d], 1)
    if isinstance(d, dict):
        return functools.reduce(lambda x, y: x * y, [len(v) if k.startswith(p) else calculate_num(v) for k, v in d.items()], 1)
    return 1


def grouper(iterable, n):
    if n == 0:
        yield iterable

    it = iter(iterable)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk
