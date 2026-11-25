# 연습 2-2 : 설명은 개념/2단계.md
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("price", type=int, nargs=2)
args = parser.parse_args()

total = 0
for num in args.price:
    total+=num

print(f"합계: {total}")

