"""여러 명령에 공통인 관심사(오류 처리, 실행 로그와 시간 측정)."""
import csv
import functools
import logging
import os
import sys
import time
from typing import Any, Callable, TypeVar, cast

from .errors import BudgetError

logger = logging.getLogger("budget_app")
F = TypeVar("F", bound=Callable[..., Any])


def log_time(func: F) -> F:
    """함수의 시작과 걸린 시간을 기록한다. --verbose일 때만 화면에 보인다."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        logger.info("%s 시작", func.__name__)
        try:
            return func(*args, **kwargs)
        finally:
            logger.info("%s 종료 (%.3f초)", func.__name__, time.perf_counter() - started)

    return cast(F, wrapper)


def _fail(message: str, hint: str = "") -> int:
    print(f"[오류] {message}", file=sys.stderr)
    if hint:
        print(f"[힌트] {hint}", file=sys.stderr)
    return 1


def handle_errors(func: Callable[..., int]) -> Callable[..., int]:
    """예외를 원인과 힌트로 바꿔 출력하고 종료 코드를 돌려준다."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> int:
        try:
            return func(*args, **kwargs)
        except BudgetError as error:
            return _fail(error.message, error.hint)
        except KeyboardInterrupt:
            print(file=sys.stderr)
            _fail("사용자가 취소했습니다.", "저장하지 않은 입력은 반영되지 않습니다.")
            return 130
        except EOFError:
            print(file=sys.stderr)
            return _fail("입력이 중간에 끝났습니다.", "모든 항목을 입력해야 저장됩니다.")
        except BrokenPipeError:
            # `list | head`처럼 받는 쪽이 먼저 닫힌 경우
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
            return 1
        except UnicodeError:
            return _fail("글자를 해석할 수 없습니다.", "파일과 입력이 UTF-8인지 확인하세요.")
        except csv.Error as error:
            return _fail(f"CSV를 해석할 수 없습니다: {error}", "CSV 형식을 확인하세요.")
        except OSError as error:
            return _fail(f"파일 처리에 실패했습니다: {error}", "경로, 권한, 디스크 용량을 확인하세요.")
        except Exception as error:
            logger.info("예상하지 못한 오류", exc_info=True)
            return _fail(f"예상하지 못한 오류입니다: {error}", "--verbose를 붙여 자세한 내용을 확인하세요.")

    return wrapper
