"""명령 해석, 대화형 입력, 화면 출력. 계산과 저장은 service에 맡긴다."""
import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, NoReturn, Optional, TypeVar

from . import validators as v
from .decorators import handle_errors
from .errors import ValidationError
from .models import Transaction, TransactionFilter
from .service import BudgetService

T = TypeVar("T")
Handler = Callable[[BudgetService, argparse.Namespace], int]
FIELDS = ("date", "type", "category", "amount", "memo", "tags")


# ---- 입력과 출력 도우미 ----
def ask(prompt: str, parse: Callable[[str], T]) -> T:
    """올바른 값이 들어올 때까지 다시 묻는다."""
    while True:
        try:
            return parse(input(prompt))
        except ValidationError as error:
            print(f"  {error.message}\n  힌트: {error.hint}")


def field_parsers(service: BudgetService) -> Dict[str, Callable[[str], Any]]:
    return {
        "date": v.parse_date,
        "type": v.parse_type,
        "category": service.check_category,
        "amount": v.parse_amount,
        "memo": v.parse_memo,
        "tags": v.parse_tags,
    }


def optional(parse: Callable[[str], T], text: Optional[str]) -> Optional[T]:
    return None if text is None else parse(text)


def format_tx(tx: Transaction) -> str:
    sign = "+" if tx.type == "income" else "-"
    parts = [tx.id, tx.date, f"{tx.type:<7}", tx.category, f"{sign}{tx.amount:,}원"]
    if tx.memo:
        parts.append(tx.memo)
    if tx.tags:
        parts.append(" ".join(f"#{tag}" for tag in tx.tags))
    return " | ".join(parts)


def print_transactions(transactions: Iterable[Transaction]) -> int:
    count = 0
    for tx in transactions:
        print(format_tx(tx))
        count += 1
    print(f"총 {count}건" if count else "데이터 없음")
    return 0


# ---- 명령 ----
def cmd_add(service: BudgetService, args: argparse.Namespace) -> int:
    names = service.require_categories()
    parsers = field_parsers(service)
    prompts = {
        "date": "날짜 (YYYY-MM-DD): ",
        "type": "타입 (income/expense): ",
        "category": f"카테고리 ({', '.join(names)}): ",
        "amount": "금액: ",
        "memo": "메모 (선택): ",
        "tags": "태그 (선택, 쉼표로 구분): ",
    }
    values = {name: ask(prompts[name], parsers[name]) for name in FIELDS}
    tx = service.add(**values)
    print(f"저장했습니다. ID: {tx.id}")
    return 0


def cmd_list(service: BudgetService, args: argparse.Namespace) -> int:
    limit = v.parse_positive(args.limit, "--limit")
    return print_transactions(service.search(TransactionFilter(), limit))


def cmd_search(service: BudgetService, args: argparse.Namespace) -> int:
    condition = TransactionFilter(
        date_from=optional(v.parse_date, args.date_from),
        date_to=optional(v.parse_date, args.date_to),
        category=optional(v.parse_category_name, args.category),
        type=optional(v.parse_type, args.type),
        query=args.query,
        tag=args.tag,
    )
    return print_transactions(service.search(condition))


def cmd_summary(service: BudgetService, args: argparse.Namespace) -> int:
    result = service.summary(v.parse_month(args.month), v.parse_positive(args.top, "--top"))
    print(f"[{result.month} 요약]")
    if result.count == 0:
        print("데이터 없음")
    else:
        print(f"총수입: {result.income:,}원")
        print(f"총지출: {result.expense:,}원")
        print(f"잔액: {result.balance:,}원")
        print(f"카테고리별 지출 TOP {args.top}")
        for rank, (name, amount) in enumerate(result.top, start=1):
            print(f"  {rank}. {name}: {amount:,}원")
        if not result.top:
            print("  지출 없음")
    if result.budget is not None:
        print(f"예산: {result.budget:,}원 (사용률 {result.budget_rate:.1f}%)")
        if result.expense > result.budget:
            print(f"[경고] 예산을 {result.expense - result.budget:,}원 초과했습니다!")
        else:
            print(f"남은 예산: {result.budget - result.expense:,}원")
    return 0


def cmd_budget_set(service: BudgetService, args: argparse.Namespace) -> int:
    month, amount = v.parse_month(args.month), v.parse_amount(args.amount)
    service.set_budget(month, amount)
    print(f"예산을 저장했습니다. {month}: {amount:,}원")
    return 0


def cmd_budget_list(service: BudgetService, args: argparse.Namespace) -> int:
    budgets = service.list_budgets(optional(v.parse_month, args.month))
    for month, amount in budgets.items():
        print(f"{month}: {amount:,}원")
    if not budgets:
        print("데이터 없음")
    return 0


def cmd_category_add(service: BudgetService, args: argparse.Namespace) -> int:
    print(f"카테고리를 추가했습니다: {service.add_category(args.name)}")
    return 0


def cmd_category_list(service: BudgetService, args: argparse.Namespace) -> int:
    names = service.categories.all()
    print("\n".join(names) if names else "데이터 없음 (추가: category add <이름>)")
    return 0


def cmd_category_remove(service: BudgetService, args: argparse.Namespace) -> int:
    print(f"카테고리를 삭제했습니다: {service.remove_category(args.name)}")
    return 0


def parse_fields(text: str) -> List[str]:
    names = [part.strip().lower() for part in text.split(",") if part.strip()]
    unknown = [name for name in names if name not in FIELDS]
    if unknown:
        raise ValidationError(f"수정할 수 없는 항목입니다: {', '.join(unknown)}", f"가능한 항목: {', '.join(FIELDS)}")
    return list(dict.fromkeys(names))


def cmd_update(service: BudgetService, args: argparse.Namespace) -> int:
    tx = service.get(args.id)
    print(format_tx(tx))
    fields = ask(f"수정할 항목 ({', '.join(FIELDS)} / 여러 개는 쉼표, 취소는 Enter): ", parse_fields)
    if not fields:
        print("수정하지 않았습니다.")
        return 0
    parsers = field_parsers(service)
    changes = {}
    for name in fields:
        current = ", ".join(tx.tags) if name == "tags" else getattr(tx, name)
        note = ", 비우려면 Enter" if name in ("memo", "tags") else ""
        changes[name] = ask(f"{name} (현재: {current}{note}): ", parsers[name])
    print(f"수정했습니다.\n{format_tx(service.update(tx, **changes))}")
    return 0


def cmd_delete(service: BudgetService, args: argparse.Namespace) -> int:
    service.delete(args.id)
    print(f"삭제했습니다. ID: {args.id}")
    return 0


def cmd_import(service: BudgetService, args: argparse.Namespace) -> int:
    print(f"{service.import_csv(Path(args.source))}건을 가져왔습니다.")
    return 0


def cmd_export(service: BudgetService, args: argparse.Namespace) -> int:
    has_range = args.date_from is not None and args.date_to is not None
    if (args.date_from is None) != (args.date_to is None) or not (args.month or has_range):
        raise ValidationError("내보낼 기간이 올바르지 않습니다.", "--month YYYY-MM 또는 --from과 --to를 함께 지정하세요.")
    condition = TransactionFilter(
        date_from=optional(v.parse_date, args.date_from),
        date_to=optional(v.parse_date, args.date_to),
        month=optional(v.parse_month, args.month),
    )
    count = service.export_csv(Path(args.out), condition)
    print(f"{count}건을 내보냈습니다: {args.out}" if count else "데이터 없음 (파일을 만들지 않았습니다.)")
    return 0


# ---- 명령 해석기 ----
class Parser(argparse.ArgumentParser):
    """하위 명령에도 같은 설정이 적용된다. 줄임 옵션은 막고 오류에는 힌트를 붙인다."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(allow_abbrev=False, **kwargs)

    def error(self, message: str) -> NoReturn:
        self.exit(2, f"[오류] 명령이 올바르지 않습니다: {message}\n[힌트] {self.prog} --help 로 사용법을 확인하세요.\n")


def build_parser() -> Parser:
    # 공통 옵션. SUPPRESS: 하위 명령의 기본값이 앞에서 받은 값을 덮어쓰지 않게 한다.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data-dir", default=argparse.SUPPRESS, help="저장 폴더 (기본: ./data)")
    common.add_argument("--verbose", action="store_true", default=argparse.SUPPRESS, help="실행 로그와 시간 출력")

    parser = Parser(prog="python -m budget_app", description="콘솔 가계부", parents=[common])
    commands = parser.add_subparsers(dest="command", metavar="<command>", required=True)

    def command(group: Any, name: str, help_text: str, handler: Optional[Handler] = None) -> Parser:
        sub = group.add_parser(name, help=help_text, description=help_text, parents=[common])
        if handler is not None:
            sub.set_defaults(handler=handler)
        return sub

    def date_range(sub: Parser) -> None:
        # from은 파이썬 예약어라 args.from으로 꺼낼 수 없어 dest를 지정한다.
        sub.add_argument("--from", dest="date_from", metavar="YYYY-MM-DD", help="시작 날짜(포함)")
        sub.add_argument("--to", dest="date_to", metavar="YYYY-MM-DD", help="종료 날짜(포함)")

    command(commands, "add", "거래 추가 (대화형)", cmd_add)

    sub = command(commands, "list", "거래 목록 (최신순)", cmd_list)
    sub.add_argument("--limit", type=int, default=10, metavar="N", help="출력할 건수 (기본: 10)")

    sub = command(commands, "search", "거래 검색 (최신순)", cmd_search)
    date_range(sub)
    sub.add_argument("--category", help="카테고리")
    sub.add_argument("--type", metavar="income|expense", help="거래 타입")
    sub.add_argument("-q", "--query", help="메모에 포함된 글자")
    sub.add_argument("--tag", help="태그")

    sub = command(commands, "summary", "월별 요약", cmd_summary)
    sub.add_argument("--month", required=True, metavar="YYYY-MM", help="요약할 월")
    sub.add_argument("--top", type=int, default=5, metavar="N", help="지출 상위 카테고리 수 (기본: 5)")

    group = command(commands, "budget", "예산 설정/조회").add_subparsers(dest="action", metavar="<action>", required=True)
    sub = command(group, "set", "월 예산 설정", cmd_budget_set)
    sub.add_argument("--month", required=True, metavar="YYYY-MM", help="대상 월")
    sub.add_argument("--amount", required=True, metavar="금액", help="예산 금액")
    sub = command(group, "list", "예산 조회", cmd_budget_list)
    sub.add_argument("--month", metavar="YYYY-MM", help="조회할 월 (생략하면 전체)")

    group = command(commands, "category", "카테고리 관리").add_subparsers(dest="action", metavar="<action>", required=True)
    command(group, "add", "카테고리 추가", cmd_category_add).add_argument("name", help="카테고리 이름")
    command(group, "list", "카테고리 목록", cmd_category_list)
    command(group, "remove", "카테고리 삭제 (사용 중이면 차단)", cmd_category_remove).add_argument("name", help="카테고리 이름")

    sub = command(commands, "update", "거래 수정 (대화형)", cmd_update)
    sub.add_argument("--id", required=True, help="수정할 거래 ID")

    sub = command(commands, "delete", "거래 삭제", cmd_delete)
    sub.add_argument("--id", required=True, help="삭제할 거래 ID")

    sub = command(commands, "import", "CSV 가져오기", cmd_import)
    sub.add_argument("--from", dest="source", required=True, metavar="CSV", help="가져올 CSV 파일")

    sub = command(commands, "export", "CSV 내보내기 (--month 또는 --from/--to 필수)", cmd_export)
    sub.add_argument("--out", required=True, metavar="CSV", help="저장할 CSV 파일 (있으면 덮어씀)")
    sub.add_argument("--month", metavar="YYYY-MM", help="내보낼 월")
    date_range(sub)
    return parser


@handle_errors
def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "verbose", False):
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="[로그] %(message)s")
    service = BudgetService(Path(getattr(args, "data_dir", "data")))
    code = args.handler(service, args)
    sys.stdout.flush()  # 파이프가 닫힌 오류를 여기서 처리한다
    return code
