# B2-1 콘솔 가계부

파일에 데이터를 저장하는 콘솔 가계부입니다. Python 3.9 이상의 표준 라이브러리만 사용합니다.

## 실행 방법

이 폴더(`과제/B2-1`)로 이동해서 실행합니다.

```bash
python -m budget_app <command> [options]
```

macOS처럼 `python` 명령이 없으면 `python3`를 사용하세요. 모든 명령은 `--help`를 지원합니다.

| 공통 옵션 | 설명 |
|---|---|
| `--data-dir <폴더>` | 저장 폴더 (기본: `./data`) |
| `--verbose` | 실행 로그와 걸린 시간 출력 |

종료 코드는 정상 `0`, 처리 오류 `1`, 잘못된 명령 형식 `2`, 사용자 취소(Ctrl+C) `130`입니다.

## 명령 예시

처음에는 카테고리가 없어 `add`가 막힙니다. `category add`부터 실행하세요.

```bash
python -m budget_app category add food
python -m budget_app category list
python -m budget_app category remove food

python -m budget_app add                      # 대화형
python -m budget_app list --limit 5           # 기본 10건
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --type expense
python -m budget_app search --category food -q 점심 --tag 회사
python -m budget_app update --id <id>         # 대화형
python -m budget_app delete --id <id>

python -m budget_app budget set --month 2024-01 --amount 500000
python -m budget_app budget list
python -m budget_app summary --month 2024-01 --top 3

python -m budget_app import --from input.csv
python -m budget_app export --out output.csv --month 2024-01
python -m budget_app export --out output.csv --from 2024-01-01 --to 2024-03-31
```

## 저장 파일

저장 형식은 JSONL(한 줄에 JSON 하나, UTF-8)이며 파일이 없으면 자동으로 만듭니다.

| 파일 | 한 줄의 형식 |
|---|---|
| `data/transactions.jsonl` | `{"id": "3f2a9c01b7de", "type": "expense", "date": "2024-01-15", "amount": 12000, "category": "food", "memo": "점심", "tags": ["회사"]}` |
| `data/categories.jsonl` | `{"name": "food"}` |
| `data/budgets.jsonl` | `{"month": "2024-01", "amount": 500000}` |

## CSV 스키마 (import/export 공통)

```csv
date,type,category,amount,memo,tags
2024-01-15,income,salary,3000000,January salary,
2024-01-16,expense,food,12000,점심,회사;외식
```

- `date`, `type`, `category`, `amount` 열은 필수이고 `memo`, `tags`는 선택입니다.
- `tags`가 여러 개면 `;`로 구분합니다.
- 인코딩은 UTF-8입니다. export는 엑셀에서 한글이 깨지지 않도록 BOM을 붙입니다.
- ID는 CSV에 없으며 import할 때 새로 만듭니다. 같은 파일을 두 번 가져오면 중복 등록됩니다.

## 정한 동작

| 항목 | 동작 |
|---|---|
| update | 대화형. 수정할 항목만 골라 다시 입력 |
| 카테고리가 없을 때 | `add`를 막고 `category add` 안내 |
| 사용 중인 카테고리 삭제 | 차단하고 사용 건수 안내 |
| 최신순 | 거래 날짜순. 날짜가 같으면 파일에서 뒤에 있는 거래 먼저 |
| 잘못된 행이 있는 import | 전체 취소하고 줄 번호와 원인 출력 |
| 금액 | 1 이상의 정수(최대 15자리, `12,000` 표기 가능) |
| `-q` | 메모에서 대소문자 구분 없이 검색 |
| export 결과 0건 | 파일을 만들지 않음 |

## 구조

| 모듈 | 책임 |
|---|---|
| `__main__.py` | 실행 진입점 |
| `cli.py` | 명령 해석, 대화형 입력, 출력 |
| `service.py` | 업무 규칙, 요약, CSV 처리 |
| `repository.py` | JSONL 읽기/쓰기 |
| `sorting.py` | 메모리를 적게 쓰는 최신순 정렬 |
| `models.py` | 데이터 구조 |
| `validators.py` | 입력 검증 |
| `decorators.py` | 오류 처리, 로그와 시간 측정 |
| `errors.py` | 오류 종류 |

- **스트리밍**: 거래 파일은 `yield`로 한 줄씩 읽습니다. `list`는 상위 N건만 힙에 보관하고, `search`는 10,000건 단위로 정렬해 임시 파일에 쓴 뒤 병합합니다.
- **안전한 저장**: 수정, 삭제, import는 임시 파일에 쓴 뒤 교체하므로 중간에 실패해도 원본이 남습니다.
- **제한**: 여러 프로세스가 동시에 쓰는 상황은 지원하지 않습니다.
