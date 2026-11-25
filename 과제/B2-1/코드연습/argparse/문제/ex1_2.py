# 연습 1-2 : 설명은 개념/1단계.md
import sys
total=0

for i in sys.argv[1:]:
    total += int(i)

print (f'합계: {total}')