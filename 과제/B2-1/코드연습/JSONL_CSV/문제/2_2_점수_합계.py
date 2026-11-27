# 설명은 개념/2단계_CSV_읽기.md
import csv
def total_score(path):
    with open(path, encoding="utf-8-sig", newline="") as file:
        sum = 0
        for line in csv.DictReader(file):
            n = int(line["score"])
            sum += n
        return sum
if __name__ == "__main__":
    from pathlib import Path
    data = Path(__file__).resolve().parent.parent / "예시자료"
    print(total_score(data / "점수.csv"))
