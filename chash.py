#!/usr/bin/env python

"""
How to hash various iterable/numpy/pandas data structures based upon content.

Notes
-----
Inspired by

https://stackoverflow.com/questions/5417949/computing-an-md5-hash-of-a-data-structure
"""

import hashlib
import numpy as np
import pandas as pd

def chash(x, alg='md5'):
    """
    Hash based upon content.

    Returns the hash of an object's content, i.e., two instances of an object
    of the same type containing identical data with the same types should have
    the same hash value.

    Parameters
    ----------
    x : object
       Data to hash.
    alg : str
       Hashing algorithm. Must be present in the hashlib library. Default
       algorithm is md5.

    Returns
    -------
    hash : str
       Computed content hash.

    Notes
    -----
    Certain user-defined class might not be content-hashable using this function.
    """

    assert alg in hashlib.algorithms
    h = getattr(hashlib, alg)(str(type(x)))

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

if __name__ == '__main__':
    from unittest import main, TestCase

    class test_chash(TestCase):
        def test_builtin(self):
            assert chash(None) == chash(None)
            assert chash(1) == chash(1)
            assert chash(1.0) == chash(1.0)
            assert chash(1L) == chash(1L)
            assert chash(1+1j) == chash(1+1j)
            assert chash(True)
            assert chash(False)
            assert chash('x')

            assert chash('xyz') == chash('xyz')
            assert chash(u'xyz') == chash(u'xyz')
            assert chash([1, 2, 3]) == chash([1, 2, 3])
            assert chash((1, 2, 3)) == chash((1, 2, 3))
            assert chash(bytearray([1, 2, 3])) == chash(bytearray([1, 2, 3]))
            assert chash(buffer('xyz')) == chash(buffer('xyz'))
            assert chash(range(5)) == chash(range(5))
            assert chash(xrange(5)) == chash(xrange(5))

            assert chash(slice(5)) == chash(slice(5))
            assert chash(slice(0, 5)) == chash(slice(0, 5))
            assert chash(slice(0, 5, 2)) == chash(slice(0, 5, 2))

            assert chash({1: 'a', 2: 'b'}) == chash({1: 'a', 2: 'b'})
            assert chash(set([1, 'a'])) == chash(set([1, 'a']))
            assert chash(frozenset([1, 'a'])) == chash(frozenset([1, 'a']))

        def test_builtin_nested(self):
            assert chash([1, 'x', [3, 4]]) == chash([1, 'x', [3, 4]])
            assert chash([1, 'x', (3, 4)]) == chash([1, 'x', (3, 4)])
            assert chash([1, 'x', (3, 4)]) == chash([1, 'x', (3, 4)])
            assert chash(set([1, 'x', (3, 4)])) == chash(set([1, 'x', (3, 4)]))

        def test_numpy(self):
            assert chash(np.bool_(True)) == chash(np.bool_(True))

            assert chash(np.int8(1)) == chash(np.int8(1))
            assert chash(np.int16(1))
            assert chash(np.int32(1))
            assert chash(np.int64(1))

            assert chash(np.uint8(1))
            assert chash(np.uint16(1))
            assert chash(np.uint32(1))
            assert chash(np.uint64(1))

            assert chash(np.float32(1)) == chash(np.float32(1))
            assert chash(np.float64(1)) == chash(np.float64(1))
            assert chash(np.float128(1)) == chash(np.float128(1))

            assert chash(np.complex64(1+1j)) == chash(np.complex64(1+1j))
            assert chash(np.complex128(1+1j)) == chash(np.complex128(1+1j))
            assert chash(np.complex256(1+1j)) == chash(np.complex256(1+1j))

            assert chash(np.datetime64('2000-01-01')) == chash(np.datetime64('2000-01-01'))
            assert chash(np.timedelta64(1,'W')) == chash(np.timedelta64(1,'W'))

            self.assertRaises(ValueError, chash, np.object())

            assert chash(np.array([[1, 2], [3, 4]])) == \
                chash(np.array([[1, 2], [3, 4]]))
            assert chash(np.array([[1, 2], [3, 4]])) != \
                chash(np.array([[1, 2], [3, 4]]).T)
            assert chash(np.array([1, 2, 3])) == chash(np.array([1, 2, 3]))
            assert chash(np.array([1, 2, 3], dtype=np.int32)) != \
                chash(np.array([1, 2, 3], dtype=np.int64))

        def test_pandas(self):
            assert chash(pd.Index([1, 2, 'a'])) == chash(pd.Index([1, 2, 'a']))
            assert chash(pd.Series([1, 2, 'a'])) == chash(pd.Series([1, 2, 'a']))
            assert chash(pd.MultiIndex(levels=[['foo'], ['mof'], [0, 1, 2]],
                                       labels=[[0, 0, 0], [0, 0, 0], [0, 1, 2]],
                                       names=['a', 'b', 'c'])) == \
                chash(pd.MultiIndex(levels=[['foo'], ['mof'], [0, 1, 2]],
                                       labels=[[0, 0, 0], [0, 0, 0], [0, 1, 2]],
                                       names=['a', 'b', 'c']))
            assert chash(pd.DataFrame(data={'a': [1, 2, 3],
                                            'b': ['x', 'y', 'z']})) == \
                chash(pd.DataFrame(data={'a': [1, 2, 3],
                                            'b': ['x', 'y', 'z']}))
        def test_other(self):
            class Foo(object):
                pass

            self.assertRaises(ValueError, chash, Foo())
    main()

    
