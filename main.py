#!/usr/bin/env python3

import argparse
from qas.framework import Framework


def main():
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=200), description="""example:
    python3 main.py --test "tmp/env/dev/sample"
""")
    parser.add_argument("-t", "--test", help="test directory")
    parser.add_argument("-c", "--case", help="case directory")
    parser.add_argument("-n", "--case-name", help="case name")
    args = parser.parse_args()

    fw = Framework(
        args.test,
        case_directory=args.case,
        case_name=args.case_name,
    )
    fw.run()


if __name__ == '__main__':
    main()
