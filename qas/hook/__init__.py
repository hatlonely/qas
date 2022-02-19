#!/usr/bin/env python3


from .hook import Hook
from .debug_hook import DebugHook
from .report_hook import ReportHook
from .email_hook import EmailHook


hook_map = {
    "debug": DebugHook,
    "report": ReportHook,
    "email": EmailHook
}

__all__ = [
    "Hook",
    "DebugHook",
    "EmailHook",
    "ReportHook",
    "hook_map",
]
