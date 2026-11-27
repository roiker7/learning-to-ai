# 설명은 개념/1단계_JSONL_쓰기와_읽기.md
import json

def to_line(movie):
    line = json.dumps(movie, ensure_ascii=False) + '\n'
    return line



if __name__ == "__main__":
    from pathlib import Path
    data = Path(__file__).resolve().parent.parent / "예시자료"
    print(repr(to_line({"title": "기생충", "score": 5})))
