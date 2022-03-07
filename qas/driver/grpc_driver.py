#!/usr/bin/env python3


import pathlib
import sys
import subprocess
import importlib
import grpc

from ..util import merge, REQUIRED
from .driver import Driver
from google.protobuf.json_format import MessageToJson, MessageToDict


class GRPCDriver(Driver):
    def __init__(self, args):
        args = merge(args, {
            "proto": REQUIRED,
            "endpoint": REQUIRED,
            "service": REQUIRED,
            "include": [],
        })
        p = pathlib.Path(args["proto"])
        self.proto_path = p
        self.generate_proto(self.proto_path, args["include"])
        self.include = args["include"]
        sys.path.append(str(p.parent.absolute()))
        self.pb2 = importlib.import_module(p.stem.replace("-", "_") + "_pb2")
        self.pb2_grpc = importlib.import_module(p.stem.replace("-", "_") + "_pb2_grpc")
        channel = grpc.insecure_channel(args["endpoint"])
        self.stub = getattr(self.pb2_grpc, args["service"] + "Stub")(channel)

    @staticmethod
    def generate_proto(proto_path, include):
        command = "python3 -m grpc_tools.protoc " \
                  "-I{directory} {include} --python_out={directory} " \
                  "--grpc_python_out={directory} {source}".format(
                    directory=str(proto_path.parent),
                    source=str(proto_path),
                    include=" ".join(["-I" + i for i in include]),
                  )
        process = subprocess.run(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.returncode != 0:
            raise Exception("{}\n{}".format(command, process.stderr))

    def name(self, req):
        return req["method"]

    def do(self, req):
        req = merge(req, {
            "method": REQUIRED,
            "type": REQUIRED,
            "args": {},
        })

        res = getattr(self.stub, req["method"])(getattr(self.pb2, req["type"])(**req["args"]))

        return MessageToDict(res)
