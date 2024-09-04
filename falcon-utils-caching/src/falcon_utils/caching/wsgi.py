import functools
import inspect
import falcon
import logging
from falcon_caching import Cache as BaseCache
from falcon_caching.options import CacheEvictionStrategy, HttpMethods
from falcon_caching.middleware import Middleware, _DECORABLE_METHOD_NAME
from .shared import CacheConfig, RequestCacheContext, CacheState
from .utils import generate_cache_key, should_cache


logger = logging.getLogger(__name__)

class CacheMiddleware(Middleware):

    def process_request(self, req, resp, *args, **kwargs):
        req.context.cache = RequestCacheContext()
    
    def process_resource(self, req: falcon.Request, resp, resource, params):
        cache_context: RequestCacheContext = req.context.cache

        if not should_cache(self.cache_config["CACHE_EVICTION_STRATEGY"], req.method):
            return

        cache_context.key = self.generate_cache_key(req)
        cache_context.state = CacheState.REQUIRES_CACHING
        
        if not self.cache.has(req.context.cache.key):
            return

        try:
            data = self.cache.get(req.context.cache.key)

            resp.media = self.deserialize(data)
            resp.status = falcon.HTTP_200
            resp.complete = True

            cache_context.state = CacheState.CACHED
        except Exception as e:
            logger.error(f"cache: deserialization failed: {e}", exc_info=1)
    
    def process_response(self, req: falcon.Request, resp, resource, req_succeeded):
        cache_context: RequestCacheContext = req.context.cache
        
        request_method = req.method.upper()

        if self.cache_config['CACHE_EVICTION_STRATEGY'] in [CacheEvictionStrategy.rest_based,
                                                            CacheEvictionStrategy.rest_and_time_based] \
            and request_method in [HttpMethods.POST,
                                       HttpMethods.PATCH,
                                       HttpMethods.PUT,
                                       HttpMethods.DELETE]:
            # get the cache key created by the GET method (assuming there was one)
            key = self.generate_cache_key(req, method='GET')
            self.cache.delete(key)
            return
        
        if cache_context.state == CacheState.CACHED:
            # since the data has been marked to cached
            return
        
        if cache_context.state == CacheState.REQUIRES_CACHING:
            try:
                value = self.serialize(req, resp, resource)
                timeout = cache_context.timeout
                if self.cache_config['CACHE_EVICTION_STRATEGY'] in [CacheEvictionStrategy.rest_based]:
                    # indefinite caching
                    timeout = 0

                self.cache.set(cache_context.key, value, timeout=timeout)

                cache_context.state = CacheState.CACHED
            except Exception as e:
                logger.error(f"cache: serialization: failed: {e}")
            

    
    def serialize(self, req, resp, resource) -> bytes:
        return super().serialize(req, resp, resource)
    
    @staticmethod
    def generate_cache_key(req, method: str = None) -> str:
        return generate_cache_key(req, method=method)


class Cache(BaseCache):
    
    @property
    def middleware(self) -> CacheMiddleware:
        """ 
        Falcon middleware integration
        """
        return CacheMiddleware(self, self.config)
    
    @staticmethod
    def cached(timeout: int, enabled=True):
        """ This is the decorator used to decorate a resource class or the requested
        method of the resource class
        """
        def cache_wrapper_decorator(class_or_func, *args):
            # is this about decorating a class or a given method?
            if inspect.isclass(class_or_func):
                cls = class_or_func
                # get all methods of the class that needs to be decorated (eg start with "on_"):
                for attr in dir(cls):
                    if callable(getattr(cls, attr)) and _DECORABLE_METHOD_NAME.match(attr):
                        method = getattr(cls, attr)                        
                        @functools.wraps(method)
                        def cache_wrapper(cls, req, resp, *args, **kwargs):
                            req.context.cache.state = CacheState.REQUIRES_CACHING if enabled else CacheState.DISABLED
                            req.context.cache.timeout = timeout
                            try:
                                method(cls, req, resp, *args, **kwargs)
                            except Exception as e:
                                req.context.cache.state = CacheState.REQUIRES_CACHING if enabled else CacheState.DISABLED
                                raise e

                        setattr(cls, attr, method)

                return cls
            else:  # this is to decorate the individual method
                func = class_or_func

                @functools.wraps(func)
                def cache_wrapper(cls, req, resp, *args, **kwargs):
                    req.context.cache.state = CacheState.REQUIRES_CACHING if enabled else CacheState.DISABLED
                    req.context.cache.timeout = timeout
                    try:
                        func(cls, req, resp, *args, **kwargs)
                    except Exception as e:
                        req.context.cache.state = CacheState.REQUIRES_CACHING if enabled else CacheState.DISABLED
                        raise e

                return cache_wrapper

        return cache_wrapper_decorator


def configure_cache(config: CacheConfig):
    return Cache(config=config.to_internal())