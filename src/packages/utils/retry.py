"""Async retry decorator with exponential backoff."""
from __future__ import annotations

import asyncio
import functools
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[F], F]:
    """Decorator that retries an async function with exponential backoff.

    Re-raises the last exception if all attempts are exhausted.
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts:
                        raise
                    await asyncio.sleep(wait)
                    wait *= backoff

        return wrapper  # type: ignore[return-value]

    return decorator
