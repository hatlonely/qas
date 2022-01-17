#!/usr/bin/env python3


import json
import yaml
import subprocess

from .default import merge, REQUIRED


class ShellDriver:
    shebang: str
    args: list[str]
    envs: dict[str, str]

    def __init__(self, args):
        args = merge(args, {
            "shebang": "/bin/bash",
            "args": ["-c"],
            "envs": dict[str, str](),
        })
        self.shebang = args["shebang"]
        self.args = args["args"]
        self.envs = args["envs"]

    def do(self, req):
        req = merge(req, {
            "command": REQUIRED,
            "envs": dict[str, str](),
            "decoder": "text",
        })

        process = subprocess.run(
            [self.shebang, *self.args, req["command"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.envs | req["envs"],
        )

        res = {
            "exitCode": process.returncode,
            "stdout": process.stdout.decode("utf-8"),
            "stderr": process.stderr.decode("utf-8"),
        }

        if req["decoder"] == "json":
            res["json"] = json.loads(res["stdout"])
        if req["decoder"] == "yaml":
            res["json"] = yaml.safe_load(res["stdout"])

        return res

