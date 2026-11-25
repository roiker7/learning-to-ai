"""제너레이터 채점기. 사용법: python3 채점.py 1  /  1_1  /  종합  (수정하지 않기)"""
import ast
import importlib.util
import inspect
import itertools
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBLEMS = {p.stem: p for p in sorted((HERE / "문제").glob("*.py"))}
FUNCTIONS = {
    "1_1": ["colors"], "1_2": ["countdown"], "2_1": ["evens"], "2_2": ["take"],
    "3_1": ["read_memos"], "3_2": ["find_lines"], "4_1": ["long_words", "add_mark"],
    "종합": ["read_temps", "hot_days", "first_n"],
}


def key_of(stem):
    return next(k for k in FUNCTIONS if stem.startswith(k))


def same(title, got, expected):
    if got != expected:
        raise AssertionError(f"{title}\n    기대: {expected}\n    실제: {got}")


def first(gen, n):
    return list(itertools.islice(gen, n))


def write(text):
    path = Path(tempfile.mkdtemp()) / "입력.txt"
    path.write_text(text, encoding="utf-8")
    return path


class Counter:
    """몇 개를 꺼내 갔는지 세는 입력."""

    def __init__(self, items):
        self.items, self.used = iter(items), 0

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self.items)
        self.used += 1
        return value


def t_1_1(m):
    same("세 색깔", list(m.colors()), ["빨강", "노랑", "파랑"])
    same("첫 값만", next(m.colors()), "빨강")


def t_1_2(m):
    same("countdown(3)", list(m.countdown(3)), [3, 2, 1])
    same("countdown(1)", list(m.countdown(1)), [1])
    same("countdown(0)", list(m.countdown(0)), [])


def t_2_1(m):
    same("짝수", list(m.evens([1, 2, 3, 4, 0])), [2, 4, 0])
    same("짝수가 없을 때", list(m.evens([1, 3])), [])
    same("끝이 없는 값", first(m.evens(itertools.count(1)), 3), [2, 4, 6])


def check_take(take):
    same("앞의 2개", list(take(["가", "나", "다"], 2)), ["가", "나"])
    same("0개", list(take(["가"], 0)), [])
    same("값이 모자랄 때", list(take(["가"], 5)), ["가"])
    source = Counter(itertools.count(1))
    same("끝이 없는 값", list(take(source, 3)), [1, 2, 3])
    if source.used > 4:
        raise AssertionError(f"필요한 것보다 많이 꺼냈습니다: {source.used}개")


def t_2_2(m):
    check_take(m.take)


def t_3_1(m):
    same("공백과 빈 줄", list(m.read_memos(write("우유\n\n  빨래  \n   \n책"))), ["우유", "빨래", "책"])
    same("빈 파일", list(m.read_memos(write(""))), [])


def t_3_2(m):
    path = write("봄날\n밤편지\n새봄\n")
    same("봄 찾기", list(m.find_lines(path, "봄")), ["봄날", "새봄"])
    same("없는 단어", list(m.find_lines(path, "눈")), [])


def t_4_1(m):
    words = ["별", "바다", "무지개"]
    same("긴 단어", list(m.long_words(words, 2)), ["바다", "무지개"])
    same("느낌표", list(m.add_mark(["별"])), ["별!"])
    same("연결", list(m.add_mark(m.long_words(words, 3))), ["무지개!"])
    source = Counter(["별", "바다", "무지개"])
    next(m.add_mark(m.long_words(source, 2)))
    same("첫 결과까지 꺼낸 개수", source.used, 2)


def t_종합(m):
    path = write("29.5\n30\n\n31.5\n28\n33\n")
    same("기온 읽기", list(m.read_temps(path)), [29.5, 30.0, 31.5, 28.0, 33.0])
    same("더운 날", list(m.hot_days([29, 30, 31], 30)), [30, 31])
    check_take(m.first_n)
    same("연결", list(m.first_n(m.hot_days(m.read_temps(path), 30), 2)), [30.0, 31.5])


def grade_one(stem):
    key, path = key_of(stem), PROBLEMS[stem]
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for name in FUNCTIONS[key]:
        if name not in functions:
            raise AssertionError(f"함수 {name}이(가) 없습니다")
        for node in ast.walk(functions[name]):
            if not isinstance(node, ast.Call):
                continue
            called = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if called in ("read", "readlines", "read_text", "list", "sorted"):
                raise AssertionError(f"{name}: {called}()은 전체를 한 번에 만듭니다. 하나씩 처리해 보세요")
    spec = importlib.util.spec_from_file_location("answer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in FUNCTIONS[key]:
        if not inspect.isgeneratorfunction(getattr(module, name)):
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
