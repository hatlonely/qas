#!/usr/bin/env python3


from .hook import Hook
from .debug_hook import DebugHook
from .trace_hook import StdoutLogHook


hook_map = {
    "debug": DebugHook,
    "stdoutLog": StdoutLogHook,
}

__all__ = ["Hook", "DebugHook", "StdoutLogHook", "hook_map"]
