#!/usr/bin/env python

from chash import chash
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

if __name__ == '__main__':
    main()
