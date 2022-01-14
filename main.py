#!/usr/bin/env python3

from qas.framework import Framework


def main():
    fw = Framework("tmp/env/ali/sample")
    fw.run()


if __name__ == '__main__':
    main()
