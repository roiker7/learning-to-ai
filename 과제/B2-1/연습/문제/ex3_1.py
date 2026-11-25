# 연습 3-1 : 설명은 개념/3단계.md
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--count", type=int, default=1)
args = parser.parse_args()
print(f'{args.name} {args.count}잔')