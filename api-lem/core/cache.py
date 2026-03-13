"""
LEM Engine - L1/L2 Caching Strategy
L1: In-memory, 60s TTL for hyper-volatile market data
L2: Redis, 1hr TTL for historical economic indicators
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Any, Callable
import asyncio
import logging

from api_lem.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None
_l1_cache: dict = {}
_l1_lock = asyncio.Lock()


def _make_key(prefix: str, *args, **kwargs) -> str:
    data = {"p": prefix, "a": args, "k": sorted(kwargs.items())}
    return f"lem:{prefix}:{hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()}"


# L1: In-memory (60s for market data)
class L1Cache:
    """In-memory cache, 60s TTL for market/volatile data"""

    TTL = settings.L1_TTL  # 60 seconds

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        async with _l1_lock:
            if key not in _l1_cache:
                return None
            entry = _l1_cache[key]
            if datetime.now() > entry["expires_at"]:
                del _l1_cache[key]
                return None
            return entry["value"]

    @classmethod
    async def set(cls, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or cls.TTL
        async with _l1_lock:
            _l1_cache[key] = {
                "value": value,
                "expires_at": datetime.now() + timedelta(seconds=ttl),
            }


# L2: Redis (1hr for historical)
class L2Cache:
    """Redis cache, 1hr TTL for historical indicators"""

    TTL = settings.L2_TTL  # 3600 seconds

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        if _redis_client is None:
            return None
        try:
            raw = await _redis_client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"L2 get error: {e}")
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if _redis_client is None:
            return
        ttl = ttl or cls.TTL
        try:
            await _redis_client.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception as e:
            logger.warning(f"L2 set error: {e}")


async def init_cache():
    """Initialize L2 (Redis) if configured"""
    global _redis_client
    if settings.REDIS_URL:
        try:
            import redis.asyncio as redis
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await _redis_client.ping()
            logger.info("L2 Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis unavailable, L2 disabled: {e}")
            _redis_client = None
    else:
        _redis_client = None


async def close_cache():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def cached(
    prefix: str,
    ttl_layer: str = "l2",  # "l1" (60s) or "l2" (3600s)
) -> Callable:
    """Decorator for caching async function results"""

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            key = _make_key(prefix, *args, **kwargs)
            layer = L1Cache if ttl_layer == "l1" else L2Cache
            val = await layer.get(key)
            if val is not None:
                return val
            try:
                result = await func(*args, **kwargs)
                await layer.set(key, result)
                return result
            except Exception:
                raise

        return wrapper

    return decorator


def cache_key(prefix: str, *args, **kwargs) -> str:
    return _make_key(prefix, *args, **kwargs)
