#!/usr/bin/env python3

import datetime
from dateutil import parser


def to_time(val) -> datetime.datetime:
    return parser.parser(val)
