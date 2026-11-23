# 연습 1-1 : 설명은 개념/1단계.md
import sys
if len(sys.argv) == 1:
    print("이름을 입력하세요")
else:
    for i in sys.argv[1:]:
        print(f"안녕, {i}!")
