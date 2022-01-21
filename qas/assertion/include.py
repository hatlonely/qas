#!/usr/bin/env python3


from datetime import datetime, timezone
from urllib.parse import urlparse
from dateutil import parser
import json


def to_time(val) -> datetime:
    return parser.parse(val)
