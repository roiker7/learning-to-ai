# 설명은 개념/3단계_파일을_한줄씩_읽기.md
def find_lines(path, word):
    # TODO
    pass



if __name__ == "__main__":
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / "예시자료" / "메모.txt"
    for line in find_lines(path, "반납"):
        print(line)
