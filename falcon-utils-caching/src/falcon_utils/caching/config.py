from dataclasses import dataclass

__all__ = ("CacheConfig",)

@dataclass(init=True)
class CacheConfig:
    is_local: bool = False
    is_async: bool = False
    key_prefix: str
    redis_url: str

    timeout: int = 0.2

    def to_internal(self) -> dict:
        return {
            'CACHE_TYPE': 'redis' if self.is_local == False else 'simple',
            'CACHE_EVICTION_STRATEGY': 'time-based',
            'CACHE_REDIS_URL': self.redis_url,
            'CACHE_KEY_PREFIX': self.key_prefix,
            'CACHE_DEFAULT_TIMEOUT': self.timeout,
            'CACHE_CONTENT_TYPE_JSON_ONLY': True
        }
