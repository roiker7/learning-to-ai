"""입력 검증. 올바르면 정리된 값을 돌려주고, 틀리면 ValidationError를 낸다.

틀렸을 때의 반응(재입력, 오류 종료, import 취소)은 호출하는 쪽이 정한다.
"""
import re
from datetime import date
from typing import Tuple

from .errors import ValidationError

TYPES = ("income", "expense")


def parse_date(text: str) -> str:
    value = text.strip()
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError
        date.fromisoformat(value)  # 2024-02-30 같은 없는 날짜도 걸러낸다
    except ValueError:
        raise ValidationError(
            f"날짜가 올바르지 않습니다: '{text}'", "YYYY-MM-DD 형식의 실제 날짜를 입력하세요. 예: 2024-01-15"
        ) from None
    return value


def parse_month(text: str) -> str:
    value = text.strip()
    try:
        parse_date(value + "-01")
    except ValidationError:
        raise ValidationError(
            f"월이 올바르지 않습니다: '{text}'", "YYYY-MM 형식으로 입력하세요. 예: 2024-01"
        ) from None
    return value


def parse_type(text: str) -> str:
    value = text.strip().lower()
    if value not in TYPES:
        raise ValidationError(f"허용되지 않은 타입입니다: '{text}'", "income 또는 expense를 입력하세요.")
    return value


def parse_amount(text: str) -> int:
    value = text.strip()
    if not re.fullmatch(r"[0-9]{1,15}|[0-9]{1,3}(,[0-9]{3}){1,4}", value):
        raise ValidationError(f"금액이 올바르지 않습니다: '{text}'", "1 이상의 정수를 입력하세요. 예: 12000")
    amount = int(value.replace(",", ""))
    if amount <= 0:
        raise ValidationError("금액은 0보다 커야 합니다.", "1 이상의 정수를 입력하세요. 예: 12000")
    return amount


def parse_memo(text: str) -> str:
    return " ".join(text.split())  # 줄바꿈이 목록 출력을 깨지 않도록 공백으로 통일


def parse_tags(text: str) -> Tuple[str, ...]:
    """쉼표나 세미콜론으로 나누고 빈 값과 중복을 없앤다."""
    tags = (parse_memo(part) for part in re.split(r"[,;]", text))
    return tuple(dict.fromkeys(tag for tag in tags if tag))


def parse_category_name(text: str) -> str:
    value = parse_memo(text)
    if not value:
        raise ValidationError("카테고리 이름이 비어 있습니다.", "한 글자 이상 입력하세요. 예: food")
    return value


def parse_positive(value: int, name: str) -> int:
    if value <= 0:
        raise ValidationError(f"{name} 값은 1 이상이어야 합니다: {value}", f"예: {name} 5")
    return value
