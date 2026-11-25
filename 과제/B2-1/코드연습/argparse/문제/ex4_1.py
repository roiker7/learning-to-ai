# 연습 4-1 : 설명은 개념/4단계.md
import argparse

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="action")

play = sub.add_parser("play")
play.add_argument("name")
play.add_argument("--volume", type=int, default=5)

stop = sub.add_parser("stop")

args = parser.parse_args()

if args.action == "play":
    print(f'재생: {args.name} (볼륨 {args.volume})')
else:
    print("정지")