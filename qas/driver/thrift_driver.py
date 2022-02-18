#!/usr/bin/env python3


import json
import pathlib
import sys
import subprocess

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.TSerialization import serialize
from thrift.protocol.TJSONProtocol import TSimpleJSONProtocolFactory

from ..util import merge, REQUIRED
from .driver import Driver


class ThriftDriver(Driver):
    def __init__(self, args):
        args = merge(args, {
            "proto": REQUIRED,
            "endpoint": REQUIRED,
            "service": REQUIRED
        })
        p = pathlib.Path(args["proto"])
        self.proto_path = p
        self.generate_proto()
        sys.path.append("{}/gen-py".format(p.parent.absolute()))

        host, port = args["endpoint"].split(":")
        socket = TSocket.TSocket(host=host, port=int(port))
        transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        transport.open()

        service = __import__("{}.{}".format(p.stem, args["service"]), fromlist=[p.stem])
        self.ttypes = __import__("{}.ttypes".format(p.stem), fromlist=[p.stem])
        self.client = getattr(service, "Client")(protocol)

    def generate_proto(self):
        command = "thrift -r --gen py {source}".format(source=str(self.proto_path.absolute()))
        process = subprocess.run(
            command.split(),
            cwd=str(self.proto_path.parent.absolute()),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.returncode != 0:
            raise Exception(process.stderr)

    def name(self, req):
        return req["method"]

    def do(self, req):
        req = merge(req, {
            "method": REQUIRED,
            "args": [],
        })

        args = []
        for arg in req["args"]:
            if isinstance(arg, dict):
                args.append(getattr(self.ttypes, arg["type"])(**arg["args"]))
            else:
                args.append(arg)
        res = getattr(self.client, req["method"])(*args)
        if hasattr(res, "write"):
            return json.loads(serialize(res, protocol_factory=TSimpleJSONProtocolFactory()))
        return res
