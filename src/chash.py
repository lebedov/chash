#!/usr/bin/env python

"""
Content-based hash.
"""

import numpy as np
import pandas as pd
import xxhash

def chash(x):
    """
    Hash based upon content.

    Returns the hash of an object's content, i.e., two instances of an object
    of the same type containing identical data with the same types should have
    the same hash value.

    Parameters
    ----------
    x : object
       Data to hash.

    Returns
    -------
    hash : str
       Computed content hash.

    Notes
    -----
    Certain user-defined class might not be content-hashable using this function.
    """

    h = xxhash.Hasher32()
    h.update(str(type(x)))

    def update(x):
        if isinstance(x, pd.Index):
            h.update(x.data)
            h.update(x.dtype.str)
        elif isinstance(x, pd.Series):
            h.update(x.data)
            h.update(x.dtype.str)
            update(x.index)
            update(x.name)
        elif isinstance(x, pd.DataFrame):
            for b in x._data.blocks:
                update(b.values)
                h.update(str(b.shape))
                h.update(b.dtype.str)
            update(x.columns)
            update(x.index)
        elif isinstance(x, np.ndarray) and x.dtype != np.dtype('O'):
            h.update(np.ascontiguousarray(x).view(np.uint8))
            h.update(str(x.shape))
            h.update(x.dtype.str)
        elif isinstance(x, dict):
            for k, v in x.iteritems():
                update(k)
                update(v)
        elif isinstance(x, basestring):
            h.update(x)
        elif np.iterable(x):
            for e in x:
                update(e)
                h.update(str(type(e)))
        elif np.isscalar(x) or x is None:
            h.update(str(x))
        elif type(x) is slice:
            h.update(str(x.start))
            h.update(str(x.stop))
            h.update(str(x.step))
        else:
            raise ValueError('type \'%s\' not content-hashable' % type(x).__name__)

    update(x)
    return h.digest()

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
