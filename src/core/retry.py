def is_rate_limit_error(error: Exception) -> bool:
    """Retorna True para erros de limite de taxa (429/RESOURCE_EXHAUSTED)."""
    for attr_name in ("status_code", "code", "status"):
        raw_value = getattr(error, attr_name, None)
        value = raw_value() if callable(raw_value) else raw_value
        if isinstance(value, int) and value == 429:
            return True
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            if normalized_value in {"429", "resource_exhausted", "too_many_requests"}:
                return True

    error_message = str(error).lower()
    return any(
        marker in error_message
        for marker in ("429", "resource_exhausted", "rate limit", "too many requests")
    )


def exponential_backoff_seconds(attempt_number: int, base_seconds: float) -> float:
    """Calcula delay com backoff exponencial por tentativa (1-indexed)."""
    safe_attempt_number = max(attempt_number, 1)
    safe_base_seconds = max(float(base_seconds), 0.0)
    return safe_base_seconds * (2 ** (safe_attempt_number - 1))
