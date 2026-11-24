# 연습 5-1 : 설명은 개념/5단계.md
import argparse
import sys

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="action")

on = sub.add_parser("on", help="켜짐")
off = sub.add_parser("off", help="꺼짐")

args = parser.parse_args()

if args.action == "on":
    print("전등 켜짐")
elif args.action == "off":
    print("전등 꺼짐")
else:
    parser.print_help()
    sys.exit(1)