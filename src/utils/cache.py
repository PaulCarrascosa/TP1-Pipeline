from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple
import time
import hashlib
import json

cache_store: Dict[str, Tuple[float, Any]] = {}
DEFAULT_EXPIRY = 300


def cache_key(*args, **kwargs) -> str:
    key_dict = {"args": str(args), "kwargs": str(kwargs)}
    key_str = json.dumps(key_dict, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache(expiry: int = DEFAULT_EXPIRY):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            now = time.time()
            if key in cache_store:
                expiry_time, value = cache_store[key]
                if expiry_time > now:
                    return value
            result = func(*args, **kwargs)
            cache_store[key] = (now + expiry, result)
            return result
        return wrapper
    return decorator


def invalidate_cache(prefix: str = None) -> None:
    global cache_store
    if prefix:
        cache_store = {k: v for k, v in cache_store.items() if not k.startswith(prefix)}
    else:
        cache_store = {}
