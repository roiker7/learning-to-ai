"""업무 규칙. 화면 출력과 input()은 사용하지 않는다."""
import csv
import uuid
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

from . import validators as v
from .decorators import log_time
from .errors import BudgetError, NotFoundError, ValidationError
from .models import Summary, Transaction, TransactionFilter
from .repository import BudgetStore, CategoryStore, TransactionRepository, atomic_writer
from .sorting import newest_first

CSV_FIELDS = ["date", "type", "category", "amount", "memo", "tags"]
CSV_REQUIRED = {"date", "type", "category", "amount"}
MAX_IMPORT_ERRORS = 20


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


class BudgetService:
    def __init__(self, data_dir: Path) -> None:
        self.transactions = TransactionRepository(data_dir)
        self.categories = CategoryStore(data_dir)
        self.budgets = BudgetStore(data_dir)

    # ---- 거래 ----
    def require_categories(self) -> List[str]:
        names = self.categories.all()
        if not names:
            raise ValidationError("등록된 카테고리가 없습니다.", "먼저 category add로 등록하세요. 예: category add food")
        return names

    def check_category(self, text: str) -> str:
        return self._check_category(text, self.require_categories())

    @staticmethod
    def _check_category(text: str, names: List[str]) -> str:
        name = v.parse_category_name(text)
        if name not in names:
            raise ValidationError(
                f"존재하지 않는 카테고리입니다: '{name}'",
                f"등록된 카테고리: {', '.join(names) or '없음'} (추가: category add <이름>)",
            )
        return name

    @log_time
    def add(self, *, date: str, type: str, category: str, amount: int, memo: str, tags: Tuple[str, ...]) -> Transaction:
        tx = Transaction(_new_id(), type, date, amount, category, memo, tags)
        self.transactions.add(tx)
        return tx

    def get(self, tx_id: str) -> Transaction:
        return self.transactions.get(tx_id)

    @log_time
    def update(self, tx: Transaction, **changes: object) -> Transaction:
        changed = replace(tx, **changes)  # type: ignore[arg-type]
        self.transactions.update(changed)
        return changed

    @log_time
    def delete(self, tx_id: str) -> None:
        self.transactions.delete(tx_id)

    def _matching(self, condition: TransactionFilter) -> Iterator[Transaction]:
        if condition.date_from and condition.date_to and condition.date_from > condition.date_to:
            raise ValidationError("시작 날짜가 종료 날짜보다 늦습니다.", "--from과 --to를 확인하세요.")
        return (tx for tx in self.transactions.iter_all() if condition.matches(tx))

    def search(self, condition: TransactionFilter, limit: Optional[int] = None) -> Iterator[Transaction]:
        return newest_first(self._matching(condition), limit)

    # ---- 요약과 예산 ----
    @log_time
    def summary(self, month: str, top: int) -> Summary:
        income = count = 0
        expenses: "Counter[str]" = Counter()
        for tx in self._matching(TransactionFilter(month=month)):
            count += 1
            if tx.type == "income":
                income += tx.amount
            else:
                expenses[tx.category] += tx.amount
        budget = self.budgets.all().get(month)
        return Summary(month, count, income, sum(expenses.values()), expenses.most_common(top), budget)

    @log_time
    def set_budget(self, month: str, amount: int) -> None:
        self.budgets.set(month, amount)

    def list_budgets(self, month: Optional[str]) -> Dict[str, int]:
        return {m: a for m, a in sorted(self.budgets.all().items()) if month in (None, m)}

    # ---- 카테고리 ----
    @log_time
    def add_category(self, text: str) -> str:
        name = v.parse_category_name(text)
        names = self.categories.all()
        if name in names:
            raise ValidationError(f"이미 있는 카테고리입니다: '{name}'", "category list로 확인하세요.")
        self.categories.save(names + [name])
        return name

    @log_time
    def remove_category(self, text: str) -> str:
        name = v.parse_category_name(text)
        names = self.categories.all()
        if name not in names:
            raise NotFoundError(f"없는 카테고리입니다: '{name}'", "category list로 확인하세요.")
        used = sum(1 for tx in self.transactions.iter_all() if tx.category == name)
        if used:
            raise ValidationError(
                f"사용 중인 카테고리라 삭제할 수 없습니다: '{name}' (거래 {used}건)",
                "update로 해당 거래의 카테고리를 바꾸거나 delete로 거래를 삭제한 뒤 다시 시도하세요.",
            )
        self.categories.save(n for n in names if n != name)
        return name

    # ---- CSV ----
    @log_time
    def import_csv(self, path: Path) -> int:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, strict=True)
            missing = CSV_REQUIRED - set(reader.fieldnames or [])
            if missing:
                raise ValidationError(
                    f"CSV에 필요한 열이 없습니다: {', '.join(sorted(missing))}",
                    f"첫 줄을 {','.join(CSV_FIELDS)} 형식으로 작성하세요.",
                )
            return self.transactions.add_many(self._parse_rows(reader))

    def _parse_rows(self, reader: "csv.DictReader[str]") -> Iterator[Transaction]:
        """행을 하나씩 검증한다. 오류가 있으면 끝에서 예외를 내 저장 전체를 취소시킨다."""
        names = self.categories.all()
        errors: List[str] = []
        error_count = 0
        for row in reader:
            try:
                yield self._parse_row(row, names)
            except BudgetError as error:
                error_count += 1
                if len(errors) < MAX_IMPORT_ERRORS:
                    errors.append(f"  {reader.line_num}번째 줄: {error.message}")
        if error_count:
            if error_count > len(errors):
                errors.append(f"  ... 외 {error_count - len(errors)}건")
            raise ValidationError(
                f"CSV 오류 {error_count}건으로 가져오기를 취소했습니다. 저장된 거래는 없습니다.\n" + "\n".join(errors),
                "표시된 줄을 고친 뒤 다시 실행하세요. 없는 카테고리는 category add로 등록하세요.",
            )

    def _parse_row(self, row: Dict[str, str], names: List[str]) -> Transaction:
        if None in row:
            raise ValidationError("열 개수가 헤더보다 많습니다.")
        get = lambda field: row.get(field) or ""  # noqa: E731
        return Transaction(
            id=_new_id(),
            type=v.parse_type(get("type")),
            date=v.parse_date(get("date")),
            amount=v.parse_amount(get("amount")),
            category=self._check_category(get("category"), names),
            memo=v.parse_memo(get("memo")),
            tags=v.parse_tags(get("tags")),
        )

    @log_time
    def export_csv(self, path: Path, condition: TransactionFilter) -> int:
        """조건에 맞는 거래를 저장하고 건수를 돌려준다. 0건이면 파일을 만들지 않는다."""
        stores = (self.transactions, self.categories, self.budgets)
        if path.resolve() in [store.file.path.resolve() for store in stores]:
            raise ValidationError("가계부 저장 파일에는 내보낼 수 없습니다.", "--out에 다른 파일 이름을 지정하세요.")
        if next(self._matching(condition), None) is None:
            return 0
        count = 0
        with atomic_writer(path, encoding="utf-8-sig") as file:  # BOM: 엑셀 한글 깨짐 방지
            writer = csv.writer(file)
            writer.writerow(CSV_FIELDS)
            for tx in self._matching(condition):
                writer.writerow([tx.date, tx.type, tx.category, tx.amount, tx.memo, ";".join(tx.tags)])
                count += 1
        return count
