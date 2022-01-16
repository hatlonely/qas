#!/usr/bin/env python3


from .default import merge, REQUIRED
import subprocess


class ShellDriver:
    shebang: str
    args: list[str]

    def __init__(self, args):
        args = merge(args, {
            "shebang": "/bin/bash",
            "args": ["-c"],
        })
        self.shebang = args["shebang"]
        self.args = args["args"]

    def do(self, req):
        req = merge(req, {
            "command": REQUIRED,
        })
        process = subprocess.run([self.shebang, *self.args, req["command"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {
            "exitCode": process.returncode,
            "stdout": process.stdout.decode("utf-8"),
            "stderr": process.stderr.decode("utf-8"),
        }

