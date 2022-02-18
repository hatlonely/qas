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
            "service": REQUIRED
        })
        p = pathlib.Path(args["proto"])
        self.proto_path = p
        self.generate_proto()
        sys.path.append(str(p.parent.absolute()))
        self.pb2 = importlib.import_module(p.stem + "_pb2")
        self.pb2_grpc = importlib.import_module(p.stem + "_pb2_grpc")
        channel = grpc.insecure_channel(args["endpoint"])
        self.stub = getattr(self.pb2_grpc, args["service"])(channel)

    def generate_proto(self):
        command = "python3 -m grpc_tools.protoc " \
                  "-I{directory} --python_out={directory} " \
                  "--grpc_python_out={directory} {source}".format(
                    directory=str(self.proto_path.parent), source=str(self.proto_path))
        subprocess.run(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

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
