"""
LEM Engine - Resilience4j-style patterns
Handles external provider timeouts without stalling user experience.
"""
import asyncio
import functools
import logging
from typing import Callable, TypeVar, ParamSpec

from api_lem.core.config import settings

logger = logging.getLogger(__name__)
P = ParamSpec("P")
T = TypeVar("T")


def resilient(
    timeout: float = None,
    max_retries: int = None,
    fallback: Callable[P, T] = None,
):
    """
    Decorator for resilient async provider calls.
    - Timeout: fail fast if provider is slow
    - Retries: retry on transient failures
    - Fallback: return fallback value on total failure
    """
    timeout = timeout or settings.PROVIDER_TIMEOUT
    max_retries = max_retries or settings.PROVIDER_MAX_RETRIES

    def decorator(func: Callable[P, T]):
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                except asyncio.TimeoutError as e:
                    last_exc = e
                    logger.warning(f"Provider timeout ({timeout}s) attempt {attempt + 1}/{max_retries}: {func.__name__}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Provider error attempt {attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))
            if fallback is not None:
                return fallback(*args, **kwargs)
            raise last_exc

        return wrapper

    return decorator
