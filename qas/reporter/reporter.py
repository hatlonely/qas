#!/usr/bin/env python3


from ..result import TestResult
from ..i18n import I18n


class Reporter:
    def __init__(self, args=None):
        self.i18n = I18n(args).i18n()

    def report(self, res: TestResult) -> str:
        return ""
