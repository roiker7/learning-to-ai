# 설명은 개념/1단계_JSONL_쓰기와_읽기.md
import json
def read_movies(path):
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.strip() == '':
                continue
            yield json.loads(line)

if __name__ == "__main__":
    from pathlib import Path
    data = Path(__file__).resolve().parent.parent / "예시자료"
    for movie in read_movies(data / "영화.jsonl"):
        print(movie)
