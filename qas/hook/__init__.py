#!/usr/bin/env python3


from .hook import Hook
from .debug_hook import DebugHook
from .trace_hook import TraceHook


hook_map = {
    "debug": DebugHook,
    "trace": TraceHook,
}

__all__ = ["Hook", "DebugHook", "TraceHook", "hook_map"]
