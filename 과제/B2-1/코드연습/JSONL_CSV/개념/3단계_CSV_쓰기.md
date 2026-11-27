# 3단계: CSV 쓰기

## `csv.writer`: 리스트 하나 = 한 줄
```python
import csv

with open("결과.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "score"])
    writer.writerow(["김, 철수", 90])
```
`결과.csv`의 내용
```
name,score
"김, 철수",90
```
- `"w"`는 쓰기 모드다. 파일이 있으면 **내용을 지우고** 새로 쓴다.
- `writer.writerow([...])`가 리스트 하나를 한 줄로 쓴다. 칸 사이 쉼표와 줄바꿈은 알아서 붙인다.
- 값에 쉼표가 있으면 **알아서 따옴표로 감싼다**. 숫자 `90`도 알아서 글자로 바꿔 쓴다.
- `encoding="utf-8-sig"`: 맨 앞에 BOM을 붙여 쓴다. 엑셀에서 열 때 한글이 깨지지 않게 하려는 것이다. 가계부의 `export`도 이렇게 한다.
- `newline=""`: 이게 없으면 윈도우에서 줄 사이에 빈 줄이 하나씩 더 생긴다. 읽기와 마찬가지로 CSV 파일에는 늘 붙인다.

## 연습문제
### 3-1 (`문제/3_1_점수표_쓰기.py`)
`write_scores(path, header, rows)`가 헤더 한 줄과 `rows`의 각 리스트를 한 줄씩 CSV로 쓴다. 엑셀용으로 BOM을 붙인다(`utf-8-sig`).

## 종합 테스트 (`문제/종합_JSONL을_CSV로.py`)
개념 파일을 닫고 푼다.
- `jsonl_to_csv(jsonl_path, csv_path, fields)`: JSONL 파일을 한 줄씩 읽어(빈 줄 건너뛰기) CSV로 옮긴다. 첫 줄은 `fields`, 그다음 줄마다 레코드에서 `fields` 순서대로 값을 꺼내 쓴다. 쓴 레코드 수를 돌려준다.
- 예: `fields`가 `["title", "score"]`이면 `{"score": 5, "title": "기생충", "year": 2019}`는 `기생충,5`가 된다.

## 말로 설명하기
- `newline=""`과 `utf-8-sig`는 각각 왜 붙이나?
- JSONL과 CSV 중 메모처럼 줄바꿈·쉼표가 들어가는 값이나 목록(태그 여러 개)을 담기 편한 것은? 이유는?
