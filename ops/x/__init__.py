from .echo_driver import EchoDriver
from .calc_driver import CalcDriver
from .echo_hook import EchoHook
from .summary_reporter import SummaryReporter
from .hello import hello


driver_map = {
    "echo": EchoDriver,
    "calc": CalcDriver,
}

hook_map = {
    "echo": EchoHook,
}

reporter_map = {
    "summary": SummaryReporter,
}


__all__ = [
    "driver_map",
    "hook_map",
    "hello",
]
