#!/usr/bin/env python3


from .driver import Driver
from .shell_driver import ShellDriver
from .mysql_driver import MysqlDriver
from .redis_driver import RedisDriver
from .mongo_driver import MongoDriver
from .http_driver import HttpDriver
from .grpc_driver import GRPCDriver
from .thrift_driver import ThriftDriver
from .elasticsearch_driver import ElasticSearchDriver
from .pop_driver import POPDriver
from .ots_driver import OTSDriver
from .mns_driver import MNSDriver
from .oss_driver import OSSDriver
from .sls_driver import SLSDriver


driver_map = {
    "http": HttpDriver,
    "grpc": GRPCDriver,
    "thrift": ThriftDriver,
    "redis": RedisDriver,
    "shell": ShellDriver,
    "mysql": MysqlDriver,
    "mongo": MongoDriver,
    "elasticsearch": ElasticSearchDriver,
    "pop": POPDriver,
    "ots": OTSDriver,
    "mns": MNSDriver,
    "oss": OSSDriver,
    "sls": SLSDriver,
}


__all__ = [
    "Driver",
    "HttpDriver",
    "GRPCDriver",
    "ThriftDriver",
    "ShellDriver",
    "MysqlDriver",
    "RedisDriver",
    "MongoDriver",
    "MNSDriver",
    "POPDriver",
    "OTSDriver",
    "OSSDriver",
    "SLSDriver",
    "driver_map",
]
