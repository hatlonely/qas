#!/usr/bin/env python3

import argparse
from qas.framework import Framework


def main():
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=200), description="""example:
    qas --test "tmp/env/ali/sample"
""")
    parser.add_argument("-t", "--test", help="test directory")
    parser.add_argument("--context", default="ctx.yaml", help="context file name")
    parser.add_argument("-c", "--case", help="case name")
    args = parser.parse_args()

    fw = Framework(args.test)
    fw.run()


if __name__ == '__main__':
    main()
