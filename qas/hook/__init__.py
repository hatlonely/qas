#!/usr/bin/env python3


from .hook import Hook
from .debug_hook import DebugHook
from .report_hook import ReportHook
from .email_hook import EmailHook
from .stdlog_hook import StdLogHook
from .slslog_hook import SLSLogHook
from .dingtalk_hook import DingTalkHook


hook_map = {
    "debug": DebugHook,
    "report": ReportHook,
    "email": EmailHook,
    "stdLog": StdLogHook,
    "slsLog": SLSLogHook,
    "dingTalk": DingTalkHook,
}

__all__ = [
    "Hook",
    "DebugHook",
    "EmailHook",
    "ReportHook",
    "StdLogHook",
    "SLSLogHook",
    "DingTalkHook",
    "hook_map",
]
