from __future__ import annotations

import typing as t
import inspect
import time
from functools import wraps


__all__ = [
    "lru_cache", 
    "CacheInfo",
]


T = t.TypeVar("T")
P = t.ParamSpec("P")


CACHE_REGISTRY: dict[str, LRUCacheFunctionWrapperBase[t.Any, t.Any]] = {}


def lru_cache(maxsize: int, ttl: int | None = None):
    """
    Re-implementation of functools.lru_cache with proper type hints and async support.
    """
    def decorator(func: t.Callable[P, T]) -> t.Callable[P, T]:
        if inspect.iscoroutinefunction(func):
            wrapper = LRUCacheAsyncFunctionWrapper(func, maxsize, ttl)
            CACHE_REGISTRY[func.__qualname__] = wrapper
            return wraps(func)(wrapper) # type: ignore
        else:
            wrapper = LRUCacheFunctionWrapper(func, maxsize, ttl)
            CACHE_REGISTRY[func.__qualname__] = wrapper
            return wraps(func)(wrapper)

    return decorator


def clear_all_caches() -> None:
    for cache in CACHE_REGISTRY.values():
        cache.cache_clear()


def get_all_cache_info() -> dict[str, CacheInfo]:
    return {
        name: cache.cache_info() 
        for name, cache in CACHE_REGISTRY.items()
    }


class CacheInfo(t.TypedDict):
    hits: int
    misses: int
    maxsize: int
    currsize: int


class CacheItem(t.Generic[T], t.NamedTuple):
    value: T
    expires_at: float | None


class LRUCache(t.Generic[T]):
    def __init__(self, capacity: int, ttl: int | None = None):
        self.capacity = capacity
        self.ttl = ttl
        self.__cache: t.OrderedDict[t.Hashable, CacheItem[T]] = t.OrderedDict()


    def probe(self, key: t.Hashable) -> bool:
        if key not in self.__cache:
            return False

        item = self.__cache[key]

        if item.expires_at is not None and item.expires_at < time.time():
            del self.__cache[key]
            return False

        return True


    def get(self, key: t.Hashable) -> T | None:
        if not self.probe(key):
            return None
        
        self.__cache.move_to_end(key)
        return self.__cache[key].value


    def insert(self, key: t.Hashable, value: T) -> None:
        if len(self.__cache) == self.capacity:
            self.__cache.popitem(last=False)

        if self.ttl is not None:
            expires_at = time.time() + self.ttl
        else:
            expires_at = None

        self.__cache[key] = CacheItem(value=value, expires_at=expires_at)
        self.__cache.move_to_end(key)


    def __len__(self) -> int:
        return len(self.__cache)


    def clear(self) -> None:
        self.__cache.clear()


class LRUCacheFunctionWrapperBase(t.Generic[P, T]):
    def __init__(self, maxsize: int, ttl: int | None = None):
        self._cache = LRUCache[T](capacity=maxsize, ttl=ttl)
        self._hits = 0
        self._misses = 0
        self._maxsize: t.Final = maxsize


    def cache_info(self) -> CacheInfo:
        return CacheInfo(
            hits=self._hits,
            misses=self._misses,
            currsize=len(self._cache),
            maxsize=self._maxsize,
        )
    

    def cache_clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0


class LRUCacheFunctionWrapper(LRUCacheFunctionWrapperBase[P, T]):
    def __init__(
            self, 
            func: t.Callable[P, T], 
            maxsize: int, 
            ttl: int | None = None,
        ):
        super().__init__(maxsize, ttl)
        self.__wrapped__ = func


    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        def wrapper():
            call_args = args + tuple(kwargs.items())

            ret = self._cache.get(call_args)

            if ret is None:
                self._misses += 1
                ret = self.__wrapped__(*args, **kwargs)
                self._cache.insert(call_args, ret)
            else:
                self._hits += 1

            return ret

        return wrapper()


class LRUCacheAsyncFunctionWrapper(LRUCacheFunctionWrapperBase[P, T]):
    def __init__(
            self, 
            func: t.Callable[P, t.Awaitable[T]], 
            maxsize: int,
            ttl: int | None = None,
        ):
        super().__init__(maxsize, ttl)
        self.__wrapped__ = func


    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> t.Awaitable[T]:
        async def wrapper():
            call_args = args + tuple(kwargs.items())

            ret = self._cache.get(call_args)

            if ret is None:
                self._misses += 1
                ret = await self.__wrapped__(*args, **kwargs)
                self._cache.insert(call_args, ret)
            else:
                self._hits += 1

            return ret

        coro = wrapper()
        return coro
