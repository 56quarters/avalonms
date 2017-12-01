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
URL = 'https://github.com/tshlabs/avalonms'
LICENSE = 'MIT'
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: BSD",
    "Operating System :: POSIX :: Linux",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Multimedia :: Sound/Audio",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5"
]


def get_contents(filename):
    with codecs.open(filename, 'rb', encoding=avalon.DEFAULT_ENCODING) as handle:
        return handle.read()


REQUIRES = [
    'flask',
    'mutagen',
    'simplejson',
    'sqlalchemy'
]


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
