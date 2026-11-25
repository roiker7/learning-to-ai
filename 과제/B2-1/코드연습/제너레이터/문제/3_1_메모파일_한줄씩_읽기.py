# 설명은 개념/3단계_파일을_한줄씩_읽기.md
def read_memos(path):
    # TODO
    pass



if __name__ == "__main__":
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / "예시자료" / "메모.txt"
    for memo in read_memos(path):
        print(memo)
