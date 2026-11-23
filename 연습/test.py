import argparse

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="action")

water = sub.add_parser("water")
water.add_argument("name")
water.add_argument("--ml", type=int, default=200)

move = sub.add_parser("move")
move.add_argument("name")
move.add_argument("--to", required=True)

status = sub.add_parser("status")

args = parser.parse_args()

if args.action == "water":
    print(f'{args.name}에 물 {args.ml}ml')
elif args.action == "move":
    print(f'{args.name} 이동: {args.to}')
elif args.action == "status":
    print("모두 건강함")