import os
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
import pickle
from typing import Any, ParamSpec, TypeVar, TypedDict


class CachedResult(TypedDict):
    arguments: dict[str, Any]
    result: Any
    added: datetime
Cache = list[CachedResult]

T = TypeVar("T")
P = ParamSpec("P")

def cache_file(
    *,
    path: str,
    lifespan: timedelta = timedelta(weeks=1)
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if os.path.isfile(path):
                with open(path, "rb") as cache_file:
                    cache_data = pickle.load(cache_file)
            else:
                cache_data: Cache = []
                
            cached_fn = cache(cache=cache_data, lifespan=lifespan)(fn)
            result = cached_fn(*args, **kwargs)

            with open(path, "wb") as cache_file:
                pickle.dump(cache_data, cache_file)

            return result

        return wrapper
    return decorator

def cache(
    *,
    cache: Cache,
    lifespan: timedelta = timedelta(weeks=1)
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            import inspect

            sig = inspect.signature(fn)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            arguments = dict(bound.arguments)
            arguments.pop("self")

            for cached_item in cache:
                if arguments == cached_item["arguments"]:
                    time_of_death = datetime.now() - lifespan
                    is_outdated = cached_item["added"] > time_of_death

                    if is_outdated:
                        cache.remove(cached_item)
                        break
                    else:
                        return cached_item["result"]

            result = fn(*args, **kwargs)

            cache.append({
                "arguments": arguments,
                "result": result,
                "added": datetime.now()
            })
            return result

        return wrapper
    return decorator