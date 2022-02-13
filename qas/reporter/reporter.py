#!/usr/bin/env python3


from ..result import TestResult


class Reporter:
    def __init__(self, args=None):
        pass

    def report(self, res: TestResult) -> str:
        return ""
