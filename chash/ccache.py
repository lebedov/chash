#!/usr/bin/env python

"""
Content-based cache.
"""

import chash
import cachetools
import functools

def _cachedmethod(cache, key_args, enabled=True):
    """
    Class instance method memoization decorator.

    Memoizes the returned value of a class instance method by hashing the
    specified arguments to the hash.

    Parameters
    ----------
    cache : dict-like
        Cache.
    key_args : int, slice, or str
        Assuming that `args` and `kwargs` respectively are the sequential
        and named parameters passed to the wrapped function, `key_args` indicates which
        of those parameters are hashed to obtain the key for
        a cached result. An int indicates an index into `args`, a slice
        indicates a tuple containing a range of elements in `args`, and a str
        indicates a single named parameter.
    enabled : bool
        If False, don't cache any results.
    """

    def decorator_disabled(method):
        return method

    def decorator_enabled(method):
        if type(key_args) in set([int, slice]):
            makekey = lambda *args, **kwargs: chash.chash(args[key_args])
        else:
            makekey = lambda *args, **kwargs: chash.chash(kwargs[key_args])
        def wrapper(self, *args, **kwargs):
            print '>', args, kwargs
            key = makekey(*args, **kwargs)
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

def lfu_cache_method(maxsize=128, key_args=0, enabled=True):
    return _cachedmethod(cachetools.LFUCache(maxsize), key_args)

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

    class Bar(object):
        @lfu_cache_method(10, key_args='x')
        def meth(self, x=1, y=2, z=3):
            return x+y+z

        def meth2(self, x, y, z):
            return x+y+z

    b = Bar()
    print b.meth(1, 2, 3)

