"""연습문제 채점기. 사용법: python3 채점.py 1  또는  python3 채점.py 1_1"""
import os
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 기대 결과: 문자열 = 이 출력과 정상 종료
HELP = "__HELP__"        # 도움말 + 종료 코드 0
ERROR = "__ERROR__"      # 사용법 안내 + 0이 아닌 종료 코드

CASES = {
    "1_1": [("민수 지우", "안녕, 민수!\n안녕, 지우!"), ("하나", "안녕, 하나!"), ("", "이름을 입력하세요")],
    "1_2": [("1 2 3", "합계: 6"), ("10", "합계: 10"), ("", "합계: 0")],
    "2_1": [("민수", "안녕, 민수!"), ("지우", "안녕, 지우!"), ("", ERROR), ("--help", HELP)],
    "2_2": [("3 5", "합계: 8"), ("10 -4", "합계: 6"), ("사과 5", ERROR), ("3", ERROR), ("--help", HELP)],
    "3_1": [("라떼 --count 2", "라떼 2잔"), ("라떼", "라떼 1잔"), ("--count 3 모카", "모카 3잔"), ("라떼 --count 둘", ERROR)],
    "3_2": [("라떼 --size L --ice", "차가운 라떼 L"), ("라떼 --size S", "따뜻한 라떼 S"), ("라떼 --size XL", ERROR), ("라떼", ERROR)],
    "3_3": [("--from 서울 --to 부산", "서울 -> 부산"), ("--to 대구 --from 대전", "대전 -> 대구"), ("--from 서울", ERROR), ("--to 부산", ERROR)],
    "4_1": [("play 봄노래 --volume 8", "재생: 봄노래 (볼륨 8)"), ("play 봄노래", "재생: 봄노래 (볼륨 5)"), ("stop", "정지"), ("stop --volume 3", ERROR), ("jump", ERROR), ("play --help", HELP)],
    "4_2": [("plus 3 5", "8"), ("repeat 하 --times 3", "하하하"), ("repeat 호", "호호"), ("plus 3", ERROR), ("repeat 하 --times 셋", ERROR)],
    "5_1": [("on", "전등 켜짐"), ("off", "전등 꺼짐"), ("", ERROR), ("--help", HELP)],
    "5_2": [("book add 어린왕자", "추가: 어린왕자"), ("book remove 어린왕자", "삭제: 어린왕자"), ("search 왕자 --limit 3", "검색: 왕자 (최대 3건)"), ("search 왕자", "검색: 왕자 (최대 10건)"), ("", ERROR), ("book", ERROR), ("book add", ERROR), ("book add --help", HELP)],
}


def run(path, text):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, str(path)] + shlex.split(text), stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8",
                          errors="replace", timeout=5, env=env)


def check(result, expected):
    if "Traceback" in result.stderr:
        return False, "오류: " + result.stderr.strip().splitlines()[-1]
    if expected == HELP:
        ok = result.returncode == 0 and "usage:" in result.stdout
        return ok, "도움말 출력과 종료 코드 0이 필요합니다"
    if expected == ERROR:
        ok = result.returncode != 0 and "usage:" in result.stdout + result.stderr
        return ok, "사용법 안내와 0이 아닌 종료 코드가 필요합니다"
    got = "\n".join(line.rstrip() for line in result.stdout.strip().splitlines())
    ok = got == expected and result.returncode == 0
    return ok, "기대 출력:\n" + expected + "\n실제 출력:\n" + got + "\n" + result.stderr.strip()


def grade(name):
    path = HERE / "문제" / f"ex{name}.py"
    print(f"\n[{name.replace('_', '-')}] 문제/{path.name}")
    source = path.read_text(encoding="utf-8") if path.exists() else ""
    if not any(line.strip() and not line.strip().startswith("#") for line in source.splitlines()):
        print("  아직 작성하지 않았습니다")
        return False
    if not name.startswith("1") and "argparse" not in source:
        print("  argparse를 사용해서 풀어 보세요")
        return False
    passed = 0
    for text, expected in CASES[name]:
        try:
            result = run(path, text)
            ok, hint = check(result, expected)
            code = result.returncode
        except subprocess.TimeoutExpired:
            ok, hint, code = False, "5초 안에 끝나지 않았습니다", "-"
        passed += ok
        print(f"  {'통과' if ok else '실패'}: ex{name}.py {text}")
        if not ok:
            print("    " + hint.strip().replace("\n", "\n    "))
            print(f"    종료 코드: {code}")
    print(f"  결과: {passed}/{len(CASES[name])}")
    return passed == len(CASES[name])


def main():
    target = sys.argv[1].replace("-", "_") if len(sys.argv) == 2 else ""
    names = [n for n in CASES if n == target or n.split("_")[0] == target]
    if not names:
        print("사용법: python3 채점.py 1  (단계) 또는 python3 채점.py 1_1  (문제)")
        return 2
    results = [grade(n) for n in names]
    print("\n모두 통과했습니다!" if all(results) else "\n아직 남은 문제가 있습니다.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
