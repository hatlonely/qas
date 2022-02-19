#!/usr/bin/env python3


from .hook import Hook
from .debug_hook import DebugHook
from .stdout_log_hook import StdoutLogHook
from .email_hook import EmailHook


hook_map = {
    "debug": DebugHook,
    "stdoutLog": StdoutLogHook,
    "email": EmailHook
}

__all__ = [
    "Hook",
    "DebugHook",
    "EmailHook",
    "StdoutLogHook",
    "hook_map",
]
