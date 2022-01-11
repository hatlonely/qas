#!/usr/bin/env python3

import yaml
import json
from src.qas.driver.http import HttpDriver
from src.qas.assertion.expect import expect_obj


drivers = {
    "http": HttpDriver
}


class Framework:
    data = None
    case = None
    ctx = dict()

    def __init__(self, filename):
        fp = open(filename, "r", encoding="utf-8")
        data = yaml.safe_load(fp)
        self.data = data
        self.case = data["case"]
        for key in data["ctx"]:
            val = data["ctx"][key]
            self.ctx[key] = drivers[val["type"]](val["args"])

    def run(self):
        for case in self.case:
            for step in case["step"]:
                # print(json.dumps(self.ctx[step["ctx"]].do(step["req"])))
                res = self.ctx[step["ctx"]].do(step["req"])
                res = expect_obj(res, step["res"])
                print(json.dumps([i.__dict__ for i in res]))
