#!/usr/bin/env python3


import datetime
import durationpy
from ..driver import merge


class RetryError(Exception):
    pass


class UntilError(Exception):
    pass


class Retry:
    attempts: int
    delay: datetime.timedelta
    condition: str

    def __init__(self, args):
        args = merge(args, {
            "attempts": 1,
            "delay": "1s",
            "cond": "",
        })
        self.attempts = args["attempts"]
        self.delay = durationpy.from_str(args["delay"])
        self.condition = args["cond"]

    def __repr__(self):
        return "cond: [{}], attempts: {}, delay: {}".format(self.condition, self.attempts, durationpy.to_str(self.delay))


class Until:
    attempts: int
    delay: datetime.timedelta
    condition: str

    def __init__(self, args):
        args = merge(args, {
            "attempts": 1,
            "delay": "1s",
            "cond": "",
        })
        self.attempts = args["attempts"]
        self.delay = durationpy.from_str(args["delay"])
        self.condition = args["cond"]

    def __repr__(self):
        return "cond: [{}], attempts: {}, delay: {}".format(self.condition, self.attempts, durationpy.to_str(self.delay))


class Dft:
    req: dict
    retry: Retry
    until: Until

    def __init__(self, args):
        args = merge(args, {
            "req": {},
            "retry": {
                "attempts": 1,
                "delay": "1s",
            },
            "until": {
                "cond": "",
                "attempts": 5,
                "delay": "1s",
            },
        })
        self.req = args["req"]
        self.retry = Retry(args["retry"])
        self.until = Until(args["until"])
