# 연습 3-2 : 설명은 개념/3단계.md
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--size", choices=['S','M','L'],required=True)
parser.add_argument("--ice", action="store_true")
args = parser.parse_args()

if args.ice == True:
    print( f'차가운 {args.name} {args.size}')
else:
    print( f'따뜻한 {args.name} {args.size}')
    