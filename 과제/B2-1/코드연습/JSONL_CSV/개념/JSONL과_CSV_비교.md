# JSONL과 CSV 비교

> 2026-11-27 학습자 요청으로 정리. 예시는 모두 실제로 실행해 확인한 결과다.

## 한 줄 요약
- **JSONL**: 프로그램이 다시 읽어서 **계산하고 처리할** 데이터. 값의 종류(숫자, 목록, 참/거짓)가 그대로 남는다.
- **CSV**: 사람이 **엑셀로 열어 볼** 표. 모든 값이 글자가 된다.

## 생김새
같은 영화 정보를 두 형식으로 저장한 모습:

**JSONL** (한 줄에 JSON 하나)
```
{"title": "괴물", "score": 4, "tags": ["가족", "스릴러"]}
{"title": "기생충", "score": 5, "tags": ["드라마"]}
```

**CSV** (첫 줄은 열 이름, 칸은 쉼표로 나눔)
```
title,score,tags
괴물,4,가족;스릴러
기생충,5,드라마
```

## 비교표
| | JSONL | CSV |
|---|---|---|
| 한 줄의 단위 | JSON 값 하나(보통 딕셔너리) | 표의 한 행 |
| 열 이름 | 줄마다 키로 들어 있음 | 첫 줄(헤더)에 한 번만 |
| 숫자 | 숫자 그대로 (`4`) | **글자** (`'4'`) → `int()` 필요 |
| 목록(태그 여러 개) | 리스트 그대로 (`["가족", "스릴러"]`) | **글자 하나로** 합쳐야 함 (`가족;스릴러`) |
| 참/거짓, 빈 값 | `true`/`false`, `null` | 글자일 뿐 |
| 줄마다 다른 항목 | 가능 (어떤 줄만 `memo`가 있어도 됨) | 모든 줄이 같은 열을 가져야 함 |
| 쉼표·줄바꿈이 든 값 | ✅ `json.dumps`가 처리 | ✅ `csv`가 따옴표로 처리 |
| 엑셀로 열기 | ❌ | ✅ |
| 파일 크기 | 키 이름이 줄마다 반복되어 더 큼 | 더 작음 |
| 한 줄씩 읽기 | ✅ | ✅ |

## 다시 읽었을 때 차이 (실행 결과)
```python
# JSONL
b = json.loads('{"title": "괴물", "score": 4, "tags": ["가족", "스릴러"]}')
b["tags"]        # ['가족', '스릴러']   ← 리스트
b["score"] + 1   # 5                   ← 바로 계산 가능

# CSV에 리스트를 그대로 넣고 다시 읽으면
# 저장: 괴물,4,"['가족', '스릴러']"
# 읽음: ['괴물', '4', "['가족', '스릴러']"]   ← 모두 글자
```

## 파이썬 코드 비교
| | JSONL | CSV |
|---|---|---|
| 모듈 | `import json` | `import csv` |
| 파일 열기(읽기) | `open(path, encoding="utf-8")` | `open(path, encoding="utf-8-sig", newline="")` |
| 파일 열기(쓰기) | `open(path, "w", encoding="utf-8")` | `open(path, "w", encoding="utf-8-sig", newline="")` |
| 한 줄 읽기 | `for line in file:` → `json.loads(line)` | `for row in csv.DictReader(file):` |
| 한 줄 쓰기 | `file.write(json.dumps(값, ensure_ascii=False) + "\n")` | `writer = csv.writer(file)` → `writer.writerow([...])` |
| 읽은 결과 | 딕셔너리 (값의 종류 그대로) | 딕셔너리 (값은 모두 글자) |
| 쓰면 안 되는 것 | 파일 전체를 `json.loads` (값이 여러 개라 `JSONDecodeError: Extra data`) | `split(",")` (따옴표 안의 쉼표까지 자름) |

## 언제 무엇을 쓰나
| 상황 | 선택 | 이유 |
|---|---|---|
| 프로그램이 다시 읽어 평균을 내고 개수를 셀 데이터 | JSONL | 숫자·목록이 그대로 남아 변환이 필요 없음 |
| 선생님이나 동료가 엑셀로 열어 볼 자료 | CSV | 엑셀에서 바로 열림 |
| AI 파인튜닝(학습) 데이터 | JSONL | 대화처럼 안에 목록이 들어간 구조를 담을 수 있음 |
| 행과 열이 고정된 단순한 표(예: 학생별 점수) | CSV | 작고 읽기 쉬움 |

## B2-1 가계부에서
- **저장 파일**(`transactions.jsonl` 등)은 **JSONL**: 태그 목록과 금액(숫자)을 그대로 보관한다. (`budget_app/repository.py`)
- **`export`**는 **CSV**: 엑셀로 보는 용도라서 태그를 `";".join(tags)`로 글자 하나로 합쳐 쓴다. (`budget_app/service.py`의 `export_csv`)
- **`import`**도 **CSV**: 읽은 값이 모두 글자라서 날짜, 금액, 태그를 하나씩 검사하고 바꾼다. (`budget_app/service.py`의 `_parse_row`)

## 스스로 점검
- CSV로 읽은 `row["score"]`에 바로 `+ 1`을 하면? → `TypeError` (글자 + 숫자)
- JSONL 한 줄을 쓸 때 끝에 `"\n"`을 빼면? → 다음 레코드가 같은 줄에 붙어 읽을 때 `Extra data` 오류
- 태그 여러 개를 CSV 한 칸에 담으려면? → `";".join(tags)`처럼 글자 하나로 합치고, 읽을 때 다시 나눔
