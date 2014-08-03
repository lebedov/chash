#!/usr/bin/env python

"""
Content-based cache.
"""

import chash
import cachetools
import functools
import inspect

def _cachedmethod(cache, key_idx=None, enabled=True):
    """Class instance method memoization decorator.

    Memoizes the returned value of a class instance method by hashing the
    specified arguments to the hash.

    Parameters
    ----------
    cache : dict-like
        Cache.
    key_idx : int or slice
        Indices indicating which of the memoized function's arguments are to be
        hashed to obtain the key for a cached result. An argument's default
        value is assumed if no value is explicitly provided.
    enabled : bool
        If False, don't cache any results.
    """

    def decorator_disabled(method):
        return method

    def decorator_enabled(method):
        argspec = inspect.getargspec(method)
        def wrapper(self, *args, **kwargs):

            # Combine all specified parameters (or their defaults) in a single
            # tuple:
            len_args = len(args)
            if argspec.defaults is not None:
                args += tuple(kwargs[k] if kwargs.has_key(k) \
                              else argspec.defaults[-(len(argspec.args)-len_args-1)+i] \
                              for i, k in enumerate(argspec.args[len_args+1:]))

            # Hash only the selected argument values:
            if key_idx is not None:
                key = chash.chash(args[key_idx])
            else:
                key = chash.chash(args)
            try:
                return cache[key]
            except KeyError:
                pass
            result = method(self, *args, **kwargs)
            cache[key] = result
            return result

        # Make the cache accessible as an attribute of the wrapped function for
        # diagnostic purposes:
        wrapper.cache = cache
        return functools.update_wrapper(wrapper, method)

    if enabled:
        return decorator_enabled
    else:
        return decorator_disabled

def lfu_cache_method(maxsize=128, key_idx=0, enabled=True):
    return _cachedmethod(cachetools.LFUCache(maxsize), key_idx)

if __name__ == '__main__':
    class Foo(object):
        @lfu_cache_method(10, 0)
        def meth(self, x, y, z):
            return x+y+z

    f = Foo()
    print f.meth(1, 2, 3)
    print f.meth.cache
    print f.meth(4, 5, 6)
    print f.meth.cache
    # This should return the result cached for arguments (1, 2, 3):
    print f.meth(1, 7, 8)
    print f.meth.cache

    print '-----'
    class Bar(object):
        @lfu_cache_method(10, 0)
        def meth(self, x=1, y=2, z=3):
            return x+y+z

    b = Bar()
    print b.meth(1, 2, 3)
    print b.meth.cache
    print b.meth(4, 5, 6)
    print b.meth.cache
    # This should return the result cached for arguments (1, 2, 3):
    print b.meth(1, 7, 8)
    print b.meth.cache

