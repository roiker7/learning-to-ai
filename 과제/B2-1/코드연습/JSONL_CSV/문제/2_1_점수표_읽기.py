# 설명은 개념/2단계_CSV_읽기.md
import csv
def read_scores(path):
    with open(path, encoding='utf-8-sig',newline="") as file:
        for line in csv.DictReader(file):
            yield line



if __name__ == "__main__":
    from pathlib import Path
    data = Path(__file__).resolve().parent.parent / "예시자료"
    for row in read_scores(data / "점수.csv"):
        print(row)
