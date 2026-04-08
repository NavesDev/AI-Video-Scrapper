import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from core.retry import exponential_backoff_seconds, is_rate_limit_error


def test_is_rate_limit_error_detects_structured_429_fields():
    class StatusCodeError(Exception):
        status_code = 429

    class CodeCallableError(Exception):
        def code(self):
            return 429

    class StatusStringError(Exception):
        status = "RESOURCE_EXHAUSTED"

    assert is_rate_limit_error(StatusCodeError("fail"))
    assert is_rate_limit_error(CodeCallableError("fail"))
    assert is_rate_limit_error(StatusStringError("fail"))


def test_is_rate_limit_error_returns_false_for_non_retryable_inputs():
    class NonRateLimitStructuredError(Exception):
        status_code = 500
        code = "INTERNAL"

    assert not is_rate_limit_error(NonRateLimitStructuredError("internal failure"))
    assert not is_rate_limit_error(Exception("request id 1429 failed"))


def test_exponential_backoff_seconds_progression_and_boundaries():
    assert exponential_backoff_seconds(attempt_number=1, base_seconds=2) == 2
    assert exponential_backoff_seconds(attempt_number=2, base_seconds=2) == 4
    assert exponential_backoff_seconds(attempt_number=3, base_seconds=2) == 8
    assert exponential_backoff_seconds(attempt_number=0, base_seconds=2) == 2
    assert exponential_backoff_seconds(attempt_number=3, base_seconds=-5) == 0
