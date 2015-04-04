# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


from __future__ import absolute_import, print_function
import sys
from glob import glob

import codecs
from os.path import join
from setuptools import setup, find_packages
import avalon


DESCRIPTION = 'Avalon Music Server'
AUTHOR = 'TSH Labs'
EMAIL = 'projects@tshlabs.org'
URL = 'http://www.tshlabs.org/'
LICENSE = 'MIT'
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: BSD",
    "Operating System :: POSIX :: Linux",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Multimedia :: Sound/Audio",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4"
]


def get_contents(filename):
    with codecs.open(filename, 'rb', encoding=avalon.DEFAULT_ENCODING) as handle:
        return handle.read()


# If this is a version of Python prior to 2.7, argparse was
# not included in the standard library and we must list it as
# an installation dependency.
_python_version = (sys.version_info[0], sys.version_info[1])
_argparse_included = (2, 7)

REQUIRES = [
    'flask',
    'mutagen',
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
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'avalon-echo-config = avalon.cli.config:main',
            'avalon-scan = avalon.cli.scan:main'
        ]
    })

