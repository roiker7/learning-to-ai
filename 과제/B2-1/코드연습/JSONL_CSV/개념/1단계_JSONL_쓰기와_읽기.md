# 1단계: JSONL 쓰기와 읽기

**JSONL**은 한 줄에 JSON 값 하나를 쓰는 형식이다. 가계부는 거래 하나를 한 줄로 저장하고, AI 학습 데이터(파인튜닝 데이터)도 이 형식을 많이 쓴다.

파이썬의 딕셔너리와 JSON 글자를 오가는 함수는 두 개다. 먼저 `import json`을 쓴다.

| 함수 | 방향 | 기억법 |
|---|---|---|
| `json.dumps(값)` | 딕셔너리 → JSON **글자** | dump + **s**(string) |
| `json.loads(글자)` | JSON 글자 → 딕셔너리 | load + **s**(string) |

## 쓰기: 딕셔너리 → 한 줄
```python
import json

movie = {"title": "기생충", "score": 5, "seen": True, "memo": None}
print(json.dumps(movie))
print(json.dumps(movie, ensure_ascii=False))
line = json.dumps(movie, ensure_ascii=False) + "\n"
print(repr(line))
```
결과
```
{"title": "기생충", "score": 5, "seen": true, "memo": null}
{"title": "기생충", "score": 5, "seen": true, "memo": null}
'{"title": "기생충", "score": 5, "seen": true, "memo": null}\n'
```
- `ensure_ascii=False`가 없으면 한글이 `기` 같은 코드로 바뀐다. 틀린 것은 아니지만 사람이 읽을 수 없다.
- 파이썬의 `True`/`None`은 JSON에서 `true`/`null`로 바뀐다.
- JSONL은 한 줄에 하나이므로 끝에 `"\n"`을 붙인다.

## 왜 직접 글자를 만들지 않고 `dumps`를 쓰나
메모에 따옴표나 줄바꿈이 들어 있으면 직접 이어 붙인 글자는 깨진다.
```python
memo = '그가 "최고"라고 했다\n두 번 봄'
print(json.dumps({"memo": memo}, ensure_ascii=False))
```
결과
```
{"memo": "그가 \"최고\"라고 했다\n두 번 봄"}
```
`dumps`는 따옴표 앞에 `\`를 붙이고, 줄바꿈을 `\n` 두 글자로 바꿔 **한 줄 안에** 넣는다. 직접 `'{"memo": "' + memo + '"}'`처럼 만들면 따옴표가 중간에 끝나고 줄도 두 개로 나뉘어 `json.loads`가 `JSONDecodeError`를 낸다.

## 읽기: 한 줄 → 딕셔너리
```python
back = json.loads('{"title": "기생충", "score": 5}\n')
print(back["title"], back["score"] + 1)
```
결과
```
기생충 6
```
`json.loads`는 줄 끝의 `\n`이나 공백은 신경 쓰지 않는다. 결과는 진짜 딕셔너리라서 `back["score"]`는 숫자 5다.

## JSONL 파일 전체 읽기 = 제너레이터 3단계 + `json.loads`
```python
def read_jsonl(path):
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.strip() == "":
                continue
            yield json.loads(line)
```
한 줄씩 읽고, 빈 줄은 건너뛰고, 줄마다 `json.loads`로 바꿔 내보낸다. 파일 전체를 `json.loads` 하면 안 된다. JSONL 파일 전체는 JSON 값 **하나**가 아니기 때문이다(이해기록 `JSON과_JSONL.md`).

## 연습문제
### 1-1 (`문제/1_1_영화를_한줄로_바꾸기.py`)
`to_line(movie)`가 딕셔너리를 JSONL 한 줄(한글 그대로, 끝에 줄바꿈)로 **돌려준다**(`return`). 제너레이터가 아니다.
### 1-2 (`문제/1_2_영화파일_읽기.py`)
`read_movies(path)`가 JSONL 파일을 한 줄씩 읽어 딕셔너리를 하나씩 내보낸다(`yield`). 빈 줄은 건너뛴다.

## 말로 설명하기
- `dumps`와 `loads`는 각각 무엇을 무엇으로 바꾸나?
- 메모에 줄바꿈이 있을 때 `dumps`를 쓰지 않고 직접 이어 붙이면 JSONL 파일에 어떤 문제가 생기나?
