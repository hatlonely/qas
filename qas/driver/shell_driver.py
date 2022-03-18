#!/usr/bin/env python3


import json
import os
import uuid

import yaml
import subprocess
import traceback

from ..util import merge, REQUIRED
from .driver import Driver


class ShellDriver(Driver):
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

    def name(self, req):
        return req["command"].split(" ")[0]

    def do(self, req):
        req = merge(req, {
            "command": REQUIRED,
            "envs": dict[str, str](),
            "decoder": "text",
            "files": dict[str, str](),
            "tmp": "/tmp",
            "clean": True,
        })

        filenames = dict([(k, "{}/{}".format(req["tmp"], uuid.uuid4().hex)) for k in req["files"]])
        for (k, v) in req["files"].items():
            with open(filenames[k], "wt", encoding='utf-8') as fp:
                fp.write(v)

        process = subprocess.run(
            [self.shebang, *self.args, req["command"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.envs | req["envs"] | filenames,
        )

        if req["clean"]:
            for filename in filenames.values():
                os.remove(filename)

        res = {
            "exitCode": process.returncode,
            "stdout": process.stdout.decode("utf-8"),
            "stderr": process.stderr.decode("utf-8"),
        }

        try:
            if req["decoder"] == "json":
                res["json"] = json.loads(res["stdout"])
            if req["decoder"] == "yaml":
                res["json"] = yaml.safe_load(res["stdout"])
        except Exception as e:
            res["err"] = traceback.format_exc()

        return res

