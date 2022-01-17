#!/usr/bin/env python3


import json
import unittest
from .shell_driver import *


# https://docs.python.org/3/library/subprocess.html
class TestSubprocess(unittest.TestCase):
    def test_bash(self):
        process = subprocess.run(["/bin/bash", "-c", "echo ${PATH}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(process.returncode, process.stdout, process.stderr)

    def test_python(self):
        process = subprocess.run(["python3", "-c", "print('hello world')"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(process.returncode, process.stdout, process.stderr)

    def test_env(self):
        process = subprocess.run(["/bin/bash", "-c", "echo ${KEY1}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={
            "KEY1": "val1"
        })
        print(process.returncode, process.stdout, process.stderr)


class TestShellDriver(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = ShellDriver(args={})

    def test_bash(self):
        res = self.driver.do(req={
            "command": "echo hello world"
        })
        print(json.dumps(res))
        self.assertDictEqual(res, {
            "exitCode": 0,
            "stdout": "hello world\n",
            "stderr": "",
        })


class TestShellDriverPython(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = ShellDriver(args={
            "shebang": "python3",
            "args": ["-c"],
        })

    def test_python(self):
        res = self.driver.do(req={
            "command": """
a = "hello"
b = "world"
print("{} {}".format(a, b))
"""
        })
        print(json.dumps(res))
        self.assertDictEqual(res, {
            "exitCode": 0,
            "stdout": "hello world\n",
            "stderr": "",
        })


if __name__ == '__main__':
    unittest.main()
