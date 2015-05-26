#!/usr/bin/env python

"""
Content-based hash.
"""

# Copyright (c) 2014-2015, Lev Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license

import inspect
import numpy as np
import pandas as pd
import xxh

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

    h = xxh.Hasher32()
    h.update(str(type(x)))

    def update(x):
        # pd.MultiIndex.data doesn't always expose the
        # same bytes for class instances with the same 
        # levels/labels/names:
        if isinstance(x, pd.MultiIndex):
            h.update(x.levels)
            h.update(x.labels)
            h.update(x.names)
        elif isinstance(x, pd.Index):
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
        elif inspect.isfunction(x):
            fc = x.func_code
            h.update(fc.co_argcount)
            h.update(fc.co_cellvars)
            h.update(fc.co_code)
            h.update(fc.co_consts)
            h.update(fc.co_flags)
            h.update(fc.co_freevars)
            h.update(fc.co_name)
            h.update(fc.co_names)
            h.update(fc.co_nlocals)
            h.update(fc.co_varnames)
        else:
            raise ValueError('type \'%s\' not content-hashable' % type(x).__name__)

    update(x)
    return h.digest()
