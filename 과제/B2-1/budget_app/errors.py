"""사용자에게 보여 줄 오류. 원인(message)과 해결 힌트(hint)를 함께 담는다."""


class BudgetError(Exception):
    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


class ValidationError(BudgetError):
    """입력값이 규칙에 맞지 않음."""


class NotFoundError(BudgetError):
    """요청한 데이터가 없음."""


class StorageError(BudgetError):
    """저장 파일을 읽거나 해석할 수 없음."""
