import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def time_calc(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        rez = func(*args, **kwargs)
        print(f'timedelta: {time.time() - start}')
        return rez
    return wrapper


def async_time_calc(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        rez = await func(*args, **kwargs)
        print(f'timedelta: {time.time() - start}')
        return rez
    return wrapper
