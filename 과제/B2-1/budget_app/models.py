"""데이터 구조. 파일이나 화면에 대해서는 모른다."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from . import validators as v


@dataclass(frozen=True)
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "memo": self.memo,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """저장된 값도 다시 검증해 손상된 데이터를 일찍 발견한다."""
        if not isinstance(data["id"], str) or not isinstance(data.get("tags", []), list):
            raise ValueError("id 또는 tags 형식 오류")
        return cls(
            id=data["id"],
            type=v.parse_type(data["type"]),
            date=v.parse_date(data["date"]),
            amount=v.parse_amount(str(data["amount"])),
            category=v.parse_category_name(data["category"]),
            memo=v.parse_memo(data.get("memo", "")),
            tags=tuple(str(tag) for tag in data.get("tags", [])),
        )


@dataclass(frozen=True)
class TransactionFilter:
    """검색 조건. None인 조건은 검사하지 않고, 나머지는 모두 만족해야 한다."""

    date_from: Optional[str] = None
    date_to: Optional[str] = None
    month: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    query: Optional[str] = None
    tag: Optional[str] = None

    def matches(self, tx: Transaction) -> bool:
        # YYYY-MM-DD는 문자열 비교 순서가 날짜 순서와 같다.
        return (
            (self.date_from is None or tx.date >= self.date_from)
            and (self.date_to is None or tx.date <= self.date_to)
            and (self.month is None or tx.date[:7] == self.month)
            and (self.category is None or tx.category == self.category)
            and (self.type is None or tx.type == self.type)
            and (self.query is None or self.query.casefold() in tx.memo.casefold())
            and (self.tag is None or self.tag in tx.tags)
        )


@dataclass(frozen=True)
class Summary:
    month: str
    count: int
    income: int
    expense: int
    top: List[Tuple[str, int]]
    budget: Optional[int]

    @property
    def balance(self) -> int:
        return self.income - self.expense

    @property
    def budget_rate(self) -> Optional[float]:
        return None if self.budget is None else self.expense / self.budget * 100
