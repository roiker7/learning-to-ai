# 연습 3-3 : 설명은 개념/3단계.md
import argparse
parser=argparse.ArgumentParser()
parser.add_argument("--from",required=True,dest="from_city")
parser.add_argument("--to",required=True)
args = parser.parse_args()
print(f'{args.from_city} -> {args.to}')