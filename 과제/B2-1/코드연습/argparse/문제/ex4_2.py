# 연습 4-2 : 설명은 개념/4단계.md
import argparse

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="action")

plus = sub.add_parser("plus")
plus.add_argument("num", nargs=2, type=int)

repeat = sub.add_parser("repeat")
repeat.add_argument("str")
repeat.add_argument("--times", default=2, type=int)

args = parser.parse_args()

if args.action == "plus":
    print(sum(args.num))
else:
    print(args.str * args.times)