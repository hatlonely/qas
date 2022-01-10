#!/usr/bin/env python3

from src.qas.framework.framework import Framework


def main():
    fw = Framework("/Users/hatlonely/hatlonely/github/hatlonely/qas/tests/test_rpc_tool.yaml")
    fw.run()


if __name__ == '__main__':
    main()
