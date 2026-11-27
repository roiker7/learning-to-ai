# 설명은 개념/3단계_CSV_쓰기.md
import csv
def write_scores(path, header, rows):
    with open(path,"w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for line in rows:
            writer.writerow(line)



if __name__ == "__main__":
    from pathlib import Path
    data = Path(__file__).resolve().parent.parent / "예시자료"
    import tempfile
    out = Path(tempfile.mkdtemp()) / "결과.csv"
    write_scores(out, ["name", "score"], [["김, 철수", 90], ["이영희", 85]])
    print(out.read_text(encoding="utf-8-sig"))
