# 연습 5-2 : 설명은 개념/5단계.md
import argparse
import sys

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="command")

book = sub.add_parser("book")
book_sub = book.add_subparsers(dest="action")

book_add = book_sub.add_parser("add", help="책 추가")
book_add.add_argument("name")

book_remove = book_sub.add_parser("remove", help="책 제거")
book_remove.add_argument("name")

search = sub.add_parser("search")
search.add_argument("name")
search.add_argument("--limit", default=10, type=int)

args = parser.parse_args()

def do_add(args):
    print(f'추가: {args}')

def do_del(args):
    print(f'삭제: {args}')

def do_srch(args_name, args_limit):
    print(f'검색: {args_name} (최대 {args_limit}건)')

if args.command == "book":
    if args.action == "add":
        do_add(args.name)
    elif args.action == "remove":
        do_del(args.name)
    else:
        book.print_help()
        sys.exit(1)
elif args.command == "search":
    do_srch(args.name, args.limit)
else:
    parser.print_help()
    sys.exit(1)