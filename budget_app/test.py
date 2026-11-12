import argparse

parser = argparse.ArgumentParser(description="연습")
sub = parser.add_subparsers(dest="command")

li = sub.add_parser("list", help="가계부 리스트 보기")
li.add_argument("--limit", type=int, default=3)

add = sub.add_parser("add",help="가계부 추가" )
add.add_argument("--add", type=str)

search = sub.add_parser("search",help="특정 가계부 찾기" )
search.add_argument("--search", type=str)

args = parser.parse_args()   
print(args)