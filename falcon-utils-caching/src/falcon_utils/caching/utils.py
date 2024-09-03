from copy import copy
from falcon_caching.options import CacheEvictionStrategy, HttpMethods


__all__ = ("generate_cache_key", "should_cache",)

def generate_cache_key(req: "falcon.Request", method: str=None):
    """ Generate the cache key from the request using the path and the method """

    path = req.path
    if path.endswith('/'):
        path = path[:-1]

    if not method:
        method = req.method

    query_key = []

    if len(req.params or {}) > 0:
        keys = list(req.params.keys())
        keys.sort()
        
        for _key in keys:
            value = req.params[_key]
            if isinstance(value, list):
                value = copy(value)
                value.sort()
                value = ",".join(value)
            query_key.append(f"{_key}:{value}")
        
        key += query_key
    
    key = f'{req.context.cache.version}:{path.lower()}:{method.lower()}:{"".join(query_key)}'

    return key

def should_cache(
    cache_eviction_strategy: str, 
    request_method: str
) -> bool:
    if cache_eviction_strategy in [CacheEvictionStrategy.rest_based,
                                   CacheEvictionStrategy.rest_and_time_based] \
        and request_method.upper() in [HttpMethods.POST,
                                    HttpMethods.PATCH,
                                    HttpMethods.PUT,
                                    HttpMethods.DELETE]:
            return False
    
    return False