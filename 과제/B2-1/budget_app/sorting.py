"""전체를 메모리에 올리지 않는 최신순 정렬."""
import heapq
import json
import tempfile
from contextlib import ExitStack
from typing import IO, Iterable, Iterator, List, Optional, Tuple

from .models import Transaction

CHUNK_SIZE = 10_000
Row = Tuple[int, Transaction]  # (파일에서의 순서, 거래)


def _key(row: Row) -> Tuple[str, int]:
    """날짜가 같으면 나중에 저장한 거래가 더 최신이다."""
    return row[1].date, row[0]


def newest_first(
    transactions: Iterable[Transaction], limit: Optional[int] = None
) -> Iterator[Transaction]:
    rows = enumerate(transactions)
    if limit is not None:
        # 힙에 상위 limit건만 보관한다.
        for _, tx in heapq.nlargest(limit, rows, key=_key):
            yield tx
        return
    # 건수를 알 수 없으면 외부 정렬: 조각마다 정렬해 임시 파일에 쓰고 한 줄씩 병합한다.
    with ExitStack() as stack:
        runs: List[Iterator[Row]] = []
        chunk: List[Row] = []
        for row in rows:
            chunk.append(row)
            if len(chunk) >= CHUNK_SIZE:
                file = stack.enter_context(tempfile.TemporaryFile("w+", encoding="utf-8"))
                _spill(chunk, file)
                runs.append(_read_run(file))
                chunk = []
        runs.append(iter(sorted(chunk, key=_key, reverse=True)))
        for _, tx in heapq.merge(*runs, key=_key, reverse=True):
            yield tx


def _spill(chunk: List[Row], file: IO[str]) -> None:
    for index, tx in sorted(chunk, key=_key, reverse=True):
        file.write(json.dumps([index, tx.to_dict()]) + "\n")
    file.seek(0)


def _read_run(file: IO[str]) -> Iterator[Row]:
    for line in file:
        index, data = json.loads(line)
        yield index, Transaction.from_dict(data)
