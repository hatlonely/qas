#!/usr/bin/env python3


from .reporter import Reporter
from .json_reporter import JsonReporter
from .text_reporter import TextReporter
from .html_reporter import HtmlReporter
from .format_step_res import format_step_res


reporter_map = {
    "text": TextReporter,
    "json": JsonReporter,
    "html": HtmlReporter,
    "none": Reporter,
}


__all__ = [
    "Reporter",
    "JsonReporter",
    "TextReporter",
    "HtmlReporter",
    "reporter_map",
    "format_step_res",
]
