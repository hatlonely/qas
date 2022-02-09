#!/usr/bin/env python3

from .json_reporter import JsonReporter
from .text_reporter import TextReporter
from .html_reporter import HtmlReporter


reporters = {
    "text": TextReporter,
    "json": JsonReporter,
    "html": HtmlReporter,
}


__all__ = ["JsonReporter", "TextReporter", "HtmlReporter", "reporters"]

