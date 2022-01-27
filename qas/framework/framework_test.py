#!/usr/bin/env python3


import unittest
import os


class TestTravel(unittest.TestCase):
    def test_travel(self):
        print([i for i in os.listdir("..") if os.path.isdir(os.path.join("..", i))])


class TestForLoop(unittest.TestCase):
    def test_for_loop(self):
        for i in range(1):
            print("body")
            break
        else:
            print("else")


if __name__ == '__main__':
    unittest.main()
