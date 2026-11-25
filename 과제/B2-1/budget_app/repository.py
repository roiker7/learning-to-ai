"""파일 저장. 거래는 한 줄씩 읽고, 수정은 임시 파일을 만든 뒤 원자적으로 교체한다."""
import json
import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, IO, Iterable, Iterator, List, Optional, Tuple

from .errors import BudgetError, NotFoundError, StorageError
from .models import Transaction
from .validators import parse_amount, parse_category_name, parse_month


@contextmanager
def atomic_writer(path: Path, encoding: str = "utf-8") -> Iterator[IO[str]]:
    """임시 파일에 모두 쓴 뒤 교체한다. 중간에 실패하면 원본은 그대로 남는다."""
    target = path.resolve()
    temp = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temp.open("x", encoding=encoding, newline="") as file:
            yield file
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, target)
    finally:
        if temp.exists():
            temp.unlink()


def _dump(record: Dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False) + "\n"


class JsonlFile:
    """한 줄에 JSON 객체 하나를 담는 파일."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)

    def corrupt(self, line_no: int, reason: object) -> StorageError:
        return StorageError(
            f"저장 파일이 손상되었습니다: {self.path} {line_no}번째 줄 ({reason})",
            "해당 줄을 고치거나 지운 뒤 다시 실행하세요. 파일은 변경하지 않았습니다.",
        )

    def read(self) -> Iterator[Tuple[int, Dict[str, Any]]]:
        """(줄 번호, 객체)를 하나씩 내보낸다. 깨진 줄은 조용히 버리지 않는다."""
        with self.path.open("rb") as file:
            for line_no, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                except ValueError as error:
                    raise self.corrupt(line_no, error) from error
                if not isinstance(data, dict):
                    raise self.corrupt(line_no, "JSON 객체가 아님")
                yield line_no, data

    def rewrite(self, records: Iterable[Dict[str, Any]]) -> None:
        with atomic_writer(self.path) as file:
            for record in records:
                file.write(_dump(record))

    def append(self, record: Dict[str, Any]) -> None:
        """끝에 한 줄 추가한다. 쓰다가 실패하면 원래 길이로 되돌린다."""
        size = self.path.stat().st_size
        try:
            with self.path.open("r+b") as file:
                prefix = b""
                if size:
                    file.seek(size - 1)
                    if file.read(1) != b"\n":  # 직접 편집해 마지막 줄바꿈이 없는 경우
                        prefix = b"\n"
                file.seek(size)
                file.write(prefix + _dump(record).encode("utf-8"))
                file.flush()
                os.fsync(file.fileno())
        except OSError:
            os.truncate(self.path, size)  # 파일이 닫힌 뒤(남은 버퍼까지 처리된 뒤) 되돌린다
            raise


class TransactionRepository:
    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "transactions.jsonl")

    def iter_all(self) -> Iterator[Transaction]:
        for line_no, data in self.file.read():
            try:
                tx = Transaction.from_dict(data)
            except (BudgetError, KeyError, TypeError, ValueError, AttributeError) as error:
                raise self.file.corrupt(line_no, error) from error
            yield tx

    def get(self, tx_id: str) -> Transaction:
        for tx in self.iter_all():
            if tx.id == tx_id:
                return tx
        raise self._not_found(tx_id)

    def add(self, tx: Transaction) -> None:
        self.file.append(tx.to_dict())

    def add_many(self, new: Iterable[Transaction]) -> int:
        """모두 저장하거나 하나도 저장하지 않는다(new에서 예외가 나면 교체하지 않음)."""
        count = 0

        def records() -> Iterator[Dict[str, Any]]:
            nonlocal count
            for tx in self.iter_all():
                yield tx.to_dict()
            for tx in new:
                count += 1
                yield tx.to_dict()

        self.file.rewrite(records())
        return count

    def update(self, changed: Transaction) -> None:
        self._replace(changed.id, changed)

    def delete(self, tx_id: str) -> None:
        self._replace(tx_id, None)

    def _replace(self, tx_id: str, replacement: Optional[Transaction]) -> None:
        def records() -> Iterator[Dict[str, Any]]:
            found = False
            for tx in self.iter_all():
                if tx.id != tx_id:
                    yield tx.to_dict()
                    continue
                found = True
                if replacement is not None:
                    yield replacement.to_dict()
            if not found:
                raise self._not_found(tx_id)

        self.file.rewrite(records())

    @staticmethod
    def _not_found(tx_id: str) -> NotFoundError:
        return NotFoundError(f"없는 데이터입니다: id={tx_id}", "list 명령으로 거래 ID를 확인하세요.")


class CategoryStore:
    """카테고리는 개수가 적으므로 한 번에 읽는다."""

    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "categories.jsonl")

    def all(self) -> List[str]:
        names = []
        for line_no, data in self.file.read():
            try:
                names.append(parse_category_name(data["name"]))
            except (BudgetError, KeyError, AttributeError) as error:
                raise self.file.corrupt(line_no, error) from error
        return names

    def save(self, names: Iterable[str]) -> None:
        self.file.rewrite({"name": name} for name in names)


class BudgetStore:
    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "budgets.jsonl")

    def all(self) -> Dict[str, int]:
        budgets = {}
        for line_no, data in self.file.read():
            try:
                budgets[parse_month(data["month"])] = parse_amount(str(data["amount"]))
            except (BudgetError, KeyError, AttributeError) as error:
                raise self.file.corrupt(line_no, error) from error
        return budgets

    def set(self, month: str, amount: int) -> None:
        budgets = self.all()
        budgets[month] = amount
        self.file.rewrite({"month": m, "amount": budgets[m]} for m in sorted(budgets))
