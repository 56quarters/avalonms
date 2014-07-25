# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


from __future__ import print_function
import sys
from glob import glob

from os.path import join
from setuptools import setup

import avalon


DESCRIPTION = 'Avalon Music Server'
AUTHOR = 'TSH Labs'
EMAIL = 'projects@tshlabs.org'
URL = 'http://www.tshlabs.org/'
LICENSE = 'MIT'
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: BSD",
    "Operating System :: POSIX :: Linux",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Multimedia :: Sound/Audio",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7"
]


def get_contents(filename):
    """Get the contents of the given file."""
    with open(filename, 'rb') as handle:
        return handle.read().decode(avalon.DEFAULT_ENCODING)


# If this is a version of Python prior to 2.7, argparse was
# not included in the standard library and we must list it as
# an installation dependency.
_python_version = (sys.version_info[0], sys.version_info[1])
_argparse_included = (2, 7)

REQUIRES = [
    'flask',
    'mutagenx',
    'simplejson',
    'sqlalchemy'
]

if _python_version < _argparse_included:
    REQUIRES.append('argparse')

README = get_contents('README.rst')

setup(
    name='avalonms',
    version=avalon.__version__,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=README,
    author_email=EMAIL,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    url=URL,
    zip_safe=False,
    install_requires=REQUIRES,
    data_files=[(join('share', 'avalonms'), glob(join('ext', '*')))],
    packages=[
        'avalon', 'avalon.app', 'avalon.cli', 'avalon.tags', 'avalon.web'],
    entry_points={
        'console_scripts': [
            'avalon-echo-config = avalon.cli.config:main',
            'avalon-scan = avalon.cli.scan:main'
        ]
    })
