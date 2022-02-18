#!usr/bin/env python3


import unittest
import pathlib
import sys
import os

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from .thrift_driver import ThriftDriver


class TestThrift(unittest.TestCase):
    def test_thrift(self):
        p = pathlib.Path("../ops/thrift/tutorial.thrift")
        x = "{}/gen-py".format(p.parent.absolute())

        sys.path.append("{}/gen-py".format(p.parent.absolute()))
        socket = TSocket.TSocket('localhost', 9090)
        transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        transport.open()

        service = __import__("tutorial.Calculator", fromlist=["tutorial"])
        ttypes = __import__("tutorial.ttypes", fromlist=["tutorial"])
        client = getattr(service, "Client")(protocol)

        res = getattr(client, "calculate")(1, getattr(ttypes, "Work")(**{
            "num1": 8,
            "num2": 4,
            "op": 3
        }))
        print(res)

        transport.close()


class TestThriftDriver(unittest.TestCase):
    def test_thrift(self):
        print(os.getcwd())
        d = ThriftDriver(args={
            "proto": "../ops/thrift/tutorial.thrift",
            "endpoint": "localhost:9090",
            "service": "Calculator",
        })

        res = d.do({
            "method": "calculate",
            "args": [
                1234,
                {
                    "type": "Work",
                    "args": {
                        "num1": 8,
                        "num2": 4,
                        "op": 3
                    }
                }
            ]
        })
        print(res)

        res = d.do({
            "method": "getStruct",
            "args": [1234],
        })
        print(res)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
