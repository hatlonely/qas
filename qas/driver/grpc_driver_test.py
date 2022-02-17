#!/usr/bin/env python3


import os
import sys
import unittest
import pathlib
import importlib
import grpc
from .grpc_driver import GRPCDriver


# 启动服务参考 https://grpc.io/docs/languages/python/basics/
# 1. 下载代码： git clone -d 1 git@github.com:grpc/grpc.git
# 2. 安装工具: pip3 install grpcio-tools
# 3. 启动服务: cd grpc/examples/python/route_guide && python3 route_guide_server.py


class TestGRPC(unittest.TestCase):
    def test_hello(self):
        a = "../ops/grpc/route_guide.proto"
        p = pathlib.Path(a)
        print(p.parent.absolute())
        print(p.stem)

    def test_grpc(self):
        p = pathlib.Path("../ops/grpc/route_guide.proto")
        sys.path.append(str(p.parent.absolute()))
        name = "route_guide"
        pb2 = importlib.import_module(name + "_pb2")
        pb2_grpc = importlib.import_module(name + "_pb2_grpc")

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = getattr(pb2_grpc, "RouteGuideStub")(channel)
            print((getattr(stub, "GetFeature"))(getattr(pb2, "Point")(**{
                "latitude": 409146138,
                "longitude": 746188906,
            })))


class TestGRPCDriver(unittest.TestCase):
    def test_grpc_driver(self):
        print(os.getcwd())
        d = GRPCDriver(args={
            "proto": "../ops/grpc/route_guide.proto",
            "endpoint": "localhost:50051",
            "service": "RouteGuideStub",
        })

        res = d.do({
            "method": "GetFeature",
            "type": "Point",
            "args": {
                "latitude": 409146138,
                "longitude": 746188906,
            }
        })

        print(res)


def main():
    unittest.main()


if __name__ == "__main__":
    main()

