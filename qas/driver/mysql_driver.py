#!/usr/bin/env python3


import pymysql

from .default import merge, REQUIRED


class MysqlDriver:
    client: pymysql.Connection

    def __init__(self, args):
        args = merge(args, {
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": REQUIRED,
            "database": REQUIRED,
        })

        self.client = pymysql.connect(
            host=args["host"],
            port=args["port"],
            user=args["username"],
            password=args["password"],
            database=args["database"],
            cursorclass=pymysql.cursors.DictCursor,
        )

    def do(self, req):
        pass
