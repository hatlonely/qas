#!/usr/bin/env python3


from .hook import Hook
from .debug_hook import DebugHook
from .report_hook import ReportHook
from .email_hook import EmailHook
from .stdlog_hook import StdLogHook


hook_map = {
    "debug": DebugHook,
    "report": ReportHook,
    "email": EmailHook,
    "stdLog": StdLogHook,
}

__all__ = [
    "Hook",
    "DebugHook",
    "EmailHook",
    "ReportHook",
    "StdLogHook",
    "hook_map",
]
