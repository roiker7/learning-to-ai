import argparse
import sys

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="command")

song = sub.add_parser("song", help="음악 추가 or 조회")
song_sub = song.add_subparsers(dest="action")

song_add = song_sub.add_parser("add", help="음악 추가")
song_add.add_argument("name", help="음악 이름")
song_add.add_argument("--artist", required=True, help="가수 이름")

song_list = song_sub.add_parser("list", help="음악 목록 개수 확인")
song_list.add_argument("--limit", default=5, type=int, help="음악 목록에 몇개 있는지 설정")

play = sub.add_parser("play", help="재생")
play.add_argument("name", help="음악 이름")
play.add_argument("--loop", action="store_true", help="반복 재생 설정")

args = parser.parse_args()

def add_song(song_name, artist_name):
    print(f'추가: {song_name} - {artist_name}')

def list_song(song_num):
    print(f'목록 {song_num}곡')

def play_song(song_name, loop_bool):
    if loop_bool == 1:
        print(f'반복 재생: {song_name}')
    else:
        print(f'재생: {song_name}')

if args.command == "song":
    if args.action == "add":
        add_song(args.name,args.artist)
    elif args.action == "list":
        list_song(args.limit)
    else:
        song.print_help()
        sys.exit(1)
        
elif args.command == "play":
    play_song(args.name, args.loop)
else:
    parser.print_help()
    sys.exit(1)