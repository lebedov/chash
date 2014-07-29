#!/usr/bin/env python

"""
Content-based cache.
"""

import cachetools
import functools

def _cachedmethod(cache, arg_idx):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            key = chash(args[arg_idx])
            try:
                return cache[key]
            except KeyError:
                pass
            result = method(self, *args, **kwargs)
            cache[key] = result
            return result
        return functools.update_wrapper(wrapper, method)
    return decorator

def lfu_cache_method(maxsize=128, arg_idx=0):
    return _cachedmethod(cachetools.LFUCache(maxsize), arg_idx)




