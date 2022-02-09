#!/usr/bin/env python3


from .shell_driver import ShellDriver
from .mysql_driver import MysqlDriver
from .redis_driver import RedisDriver
from .mongo_driver import MongoDriver
from .http_driver import HttpDriver
from .pop_driver import POPDriver
from .ots_driver import OTSDriver
from .mns_driver import MNSDriver
from .oss_driver import OSSDriver
from .default import merge, REQUIRED


drivers = {
    "http": HttpDriver,
    "redis": RedisDriver,
    "shell": ShellDriver,
    "mysql": MysqlDriver,
    "mongo": MongoDriver,
    "pop": POPDriver,
    "ots": OTSDriver,
    "mns": MNSDriver,
    "oss": OSSDriver,
}


__all__ = [
    "HttpDriver",
    "ShellDriver",
    "MysqlDriver",
    "RedisDriver",
    "MongoDriver",
    "MNSDriver",
    "POPDriver",
    "OTSDriver",
    "OSSDriver",
    "merge",
    "REQUIRED",
    "drivers",
]
