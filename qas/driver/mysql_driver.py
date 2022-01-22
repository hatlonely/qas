#!/usr/bin/env python3


import pymysql

from .default import merge, REQUIRED


class MysqlDriver:
    connection: pymysql.Connection

    def __init__(self, args):
        args = merge(args, {
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": REQUIRED,
            "database": REQUIRED,
        })

        self.connection = pymysql.connect(
            host=args["host"],
            port=args["port"],
            user=args["username"],
            password=args["password"],
            database=args["database"],
            cursorclass=pymysql.cursors.DictCursor,
        )

    def do(self, req):
        req = merge(req, {
            "action": "sql",
            "sql": REQUIRED,
            "args": [],
        })

        do_map = {
            "sql": self.sql,
            "fetchone": self.fetchone,
            "fetchall": self.fetchall,
        }
        if req["action"] not in do_map:
            raise Exception("unsupported action [{}]".format(req["action"]))

        try:
            return do_map[req["action"]](req)
        except pymysql.err.OperationalError as e:
            return {
                "code": "OperationalError",
                "err": {
                    "type": "OperationalError",
                    "args": e.args
                },
            }
        except Exception as e:
            raise e

    def sql(self, req):
        with self.connection.cursor() as cursor:
            cursor.execute(req["sql"], req["args"])
        self.connection.commit()
        return {
            "code": "OK"
        }

    def fetchone(self, req):
        with self.connection.cursor() as cursor:
            cursor.execute(req["sql"], req["args"])
            result = cursor.fetchone()
        self.connection.commit()
        return {
            "code": "OK",
            "res": result
        }

    def fetchall(self, req):
        with self.connection.cursor() as cursor:
            cursor.execute(req["sql"], req["args"])
            result = cursor.fetchall()
        self.connection.commit()
        return {
            "code": "OK",
            "res": result
        }
