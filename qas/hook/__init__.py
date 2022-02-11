#!/usr/bin/env python3

from .debug_hook import DebugHook
from .trace_hook import TraceHook


hook_map = {
    "debug": DebugHook,
    "trace": TraceHook,
}

__all__ = ["DebugHook", "TraceHook", "hook_map"]
