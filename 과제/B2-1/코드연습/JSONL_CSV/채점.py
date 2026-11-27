"""JSONL/CSV 채점기. 사용법: python3 채점.py 1  /  1_1  /  종합  (수정하지 않기)"""
import ast
import csv
import importlib.util
import inspect
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBLEMS = {p.stem: p for p in sorted((HERE / "문제").glob("*.py"))}
FUNCTIONS = {"1_1": ["to_line"], "1_2": ["read_movies"], "2_1": ["read_scores"],
             "2_2": ["total_score"], "3_1": ["write_scores"], "종합": ["jsonl_to_csv"]}
GENERATORS = {"read_movies", "read_scores"}
BANNED = ("read", "readlines", "read_text", "split", "splitlines")


def key_of(stem):
    return next(k for k in FUNCTIONS if stem.startswith(k))


def same(title, got, expected):
    if got != expected:
        raise AssertionError(f"{title}\n    기대: {expected!r}\n    실제: {got!r}")


def new_path(name):
    return Path(tempfile.mkdtemp()) / name


def write(name, text, encoding="utf-8"):
    path = new_path(name)
    path.write_bytes(text.encode(encoding))
    return path


def read_csv(path):
    raw = path.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise AssertionError("CSV 맨 앞에 BOM이 없습니다. encoding을 확인하세요")
    with open(path, encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def t_1_1(m):
    line = m.to_line({"title": "기생충", "score": 5})
    same("기본", line, '{"title": "기생충", "score": 5}\n')
    tricky = {"memo": '그가 "최고"라고 했다\n두 번 봄', "seen": True, "tags": ["가족", "스릴러"]}
    line = m.to_line(tricky)
    same("줄바꿈 개수(끝에 하나만)", line.count("\n"), 1)
    try:
        same("따옴표·줄바꿈이 든 값 되돌리기", json.loads(line), tricky)
    except ValueError as error:
        raise AssertionError(f"올바른 JSON이 아닙니다: {error}")


def t_1_2(m):
    path = write("영화.jsonl", '{"title": "A", "score": 3}\n\n{"title": "나", "memo": "x, \\"y\\""}\n')
    same("읽기", list(m.read_movies(path)), [{"title": "A", "score": 3}, {"title": "나", "memo": 'x, "y"'}])
    path = write("영화.jsonl", '{"title": "A"}\n{"title": "B"}\n이 줄은 깨짐\n')
    gen = m.read_movies(path)
    same("깨진 줄 앞의 2개는 먼저 꺼낼 수 있어야 함(한 줄씩)", [next(gen), next(gen)], [{"title": "A"}, {"title": "B"}])


def t_2_1(m):
    path = write("점수.csv", 'name,score\r\n"김, 철수",90\r\n이영희,85\r\n', "utf-8-sig")
    same("BOM과 쉼표", list(m.read_scores(path)), [{"name": "김, 철수", "score": "90"}, {"name": "이영희", "score": "85"}])
    path = write("점수.csv", "name,score\n박민수,70\n")
    same("BOM 없는 파일", list(m.read_scores(path)), [{"name": "박민수", "score": "70"}])


def t_2_2(m):
    path = write("점수.csv", 'name,score\r\n"김, 철수",90\r\n이영희,85\r\n', "utf-8-sig")
    same("합계", m.total_score(path), 175)
    same("헤더만", m.total_score(write("점수.csv", "name,score\n", "utf-8-sig")), 0)


def t_3_1(m):
    path = new_path("결과.csv")
    m.write_scores(path, ["name", "score"], [["김, 철수", 90], ["이영희", 85]])
    same("쓴 내용", read_csv(path), [["name", "score"], ["김, 철수", "90"], ["이영희", "85"]])
    m.write_scores(path, ["name"], [])
    same("다시 쓰면 덮어씀", read_csv(path), [["name"]])


def t_종합(m):
    src = write("영화.jsonl", '{"score": 5, "title": "기생충", "year": 2019}\n\n'
                '{"title": "괴물", "score": 4, "memo": "x"}\n{"title": "한강, \\"밤\\"", "score": 3}\n')
    out = new_path("영화.csv")
    same("돌려준 건수", m.jsonl_to_csv(src, out, ["title", "score"]), 3)
    same("CSV 내용", read_csv(out), [["title", "score"], ["기생충", "5"], ["괴물", "4"], ['한강, "밤"', "3"]])
    out = new_path("영화.csv")
    same("열 순서 바꾸기", (m.jsonl_to_csv(src, out, ["score"]), read_csv(out)[:2]), (3, [["score"], ["5"]]))


def grade_one(stem):
    key, path = key_of(stem), PROBLEMS[stem]
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for name in FUNCTIONS[key]:
        if name not in functions:
            raise AssertionError(f"함수 {name}이(가) 없습니다")
        for node in ast.walk(functions[name]):
            if isinstance(node, ast.Call):
                called = getattr(node.func, "attr", getattr(node.func, "id", ""))
                if called in BANNED:
                    raise AssertionError(f"{name}: {called}()은 쓰지 않습니다. 한 줄씩 읽고 json/csv 모듈로 처리하세요")
    spec = importlib.util.spec_from_file_location("answer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in FUNCTIONS[key]:
        if name in GENERATORS and not inspect.isgeneratorfunction(getattr(module, name)):
            raise AssertionError(f"{name}: 아직 작성하지 않았거나 yield가 없습니다")
    globals()["t_" + key](module)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--one":
        try:
            grade_one(sys.argv[2])
        except AssertionError as error:
            print("  " + str(error))
            sys.exit(1)
        except Exception as error:
            print(f"  오류: {type(error).__name__}: {error}")
            sys.exit(1)
        return
    want = sys.argv[1] if len(sys.argv) == 2 else ""
    chosen = [s for s in PROBLEMS if want and (key_of(s) == want or s.startswith(want + "_"))]
    if not chosen:
        print("사용법: python3 채점.py 1  /  1_1  /  종합")
        sys.exit(1)
    failed = 0
    for stem in chosen:
        print(f"[{stem}]")
        try:
            done = subprocess.run([sys.executable, "-B", __file__, "--one", stem], timeout=5)
            ok = done.returncode == 0
        except subprocess.TimeoutExpired:
            print("  5초 안에 끝나지 않았습니다. 끝없이 반복하는지 확인하세요")
            ok = False
        print("  통과" if ok else "  다시 해 보세요", flush=True)
        failed += not ok
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
