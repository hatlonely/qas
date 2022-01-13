#!/usr/bin/env python3

from src.qas.framework import Framework


def main():
    fw = Framework("tests/test_pop.yaml")
    fw.run()


if __name__ == '__main__':
    main()
