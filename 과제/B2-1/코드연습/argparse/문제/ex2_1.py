# 연습 2-1 : 설명은 개념/2단계.md
import argparse
parse = argparse.ArgumentParser()
parse.add_argument("name", help="name", type=str)
args = parse.parse_args()

print(f'안녕, {args.name}!')