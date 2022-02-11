#!/usr/bin/env python3

from .debug_hook import DebugHook


hook_map = {
    "debug": DebugHook,
}

__all__ = ["DebugHook", "hook_map"]
