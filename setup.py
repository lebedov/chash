#!/usr/bin/env python

import os

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup

NAME =             'chash'
VERSION =          '0.1.0'
AUTHOR =           'Lev Givon'
AUTHOR_EMAIL =     'lev@columbia.edu'
URL =              'https://github.com/lebedov/chash'
MAINTAINER =       AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
DESCRIPTION =      'Content-based hash'
LONG_DESCRIPTION = DESCRIPTION
DOWNLOAD_URL =     URL
LICENSE =          'BSD'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development']

if __name__ == '__main__':
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email = AUTHOR_EMAIL,
      url = URL,
      maintainer = MAINTAINER,
      maintainer_email = MAINTAINER_EMAIL,
      description = DESCRIPTION,
      license = LICENSE,
      classifiers = CLASSIFIERS,
      package_dir = {'src': 'src'},
      packages = ['src'],
      test_suite = 'tests',
      install_requires = [
          'numpy',
          'pandas',
          'xxhash' 
          ])
