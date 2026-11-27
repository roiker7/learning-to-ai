# 2단계: CSV 읽기

**CSV**는 쉼표로 칸을 나눈 표 형식이다. 엑셀에서 열고 저장할 수 있어서 데이터를 주고받을 때 많이 쓴다. 가계부의 `import`/`export`, AI의 표 형태 데이터가 이 형식이다.

```
name,score          ← 첫 줄: 열 이름(헤더)
"김, 철수",90        ← 값에 쉼표가 있으면 따옴표로 감싼다
이영희,85
```

## `split(",")`로 나누면 안 되는 이유
```python
print('"김, 철수",90'.split(","))
```
결과
```
['"김', ' 철수"', '90']
```
따옴표 안의 쉼표까지 잘라 버린다. 그래서 `import csv`의 `csv` 모듈을 쓴다. 따옴표, 줄바꿈이 든 값 같은 규칙을 알아서 처리한다.

## `csv.DictReader`: 한 줄을 딕셔너리로
```python
import csv

with open("예시자료/점수.csv", encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        print(row)
```
결과
```
{'name': '김, 철수', 'score': '90'}
{'name': '이영희', 'score': '85'}
```
- 첫 줄(헤더)을 열 이름으로 쓰고, 그다음 줄부터 하나씩 딕셔너리로 꺼낸다. 파일처럼 **한 줄씩** 나오므로 큰 파일도 괜찮다.
- **값은 모두 글자**다. `'90'`은 숫자가 아니다. 계산하려면 `int(row["score"])`로 바꾼다.

## `open`에 붙는 두 가지
| 쓰는 것 | 이유 |
|---|---|
| `encoding="utf-8-sig"` | 엑셀이 저장한 CSV는 맨 앞에 보이지 않는 표시(BOM, 3바이트)가 붙어 있다. `utf-8-sig`는 이것을 떼고 읽는다. 없어도 그대로 읽는다 |
| `newline=""` | 줄바꿈 처리를 `csv` 모듈에 맡긴다. 파이썬 공식 문서가 CSV 파일을 열 때 이렇게 하라고 안내한다 |

BOM이 있는 파일을 `utf-8`로 읽으면 첫 열 이름이 망가진다.
```python
with open("예시자료/점수.csv", encoding="utf-8", newline="") as file:
    print(next(csv.DictReader(file)))
```
결과
```
{'﻿name': '김, 철수', 'score': '90'}
```
열 이름이 `'name'`이 아니라 `'﻿name'`이 되어 `row["name"]`이 `KeyError`를 낸다.

## 연습문제
### 2-1 (`문제/2_1_점수표_읽기.py`)
`read_scores(path)`가 CSV를 한 줄씩 읽어 딕셔너리를 하나씩 내보낸다(`yield`). 채점 파일에는 BOM과 쉼표가 든 이름이 있다.
### 2-2 (`문제/2_2_점수_합계.py`)
`total_score(path)`가 `score` 열을 모두 더한 **숫자**를 돌려준다(`return`). 헤더만 있으면 0.

## 말로 설명하기
- CSV를 `split(",")`로 나누면 언제 틀리나?
- `DictReader`가 돌려준 `row["score"]`로 바로 더하기를 하면 어떻게 되나?
