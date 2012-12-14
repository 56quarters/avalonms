#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import print_function

import os
import os.path
import re
import subprocess
import sys

from setuptools import setup, find_packages


AUTHOR = 'TSH Labs'
DESCRIPTION = 'Avalon Music Server'
EMAIL = 'projects@tshlabs.org'
URL = 'http://www.tshlabs.org/'
LICENSE = 'BSD'
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: BSD License",
    "Operating System :: POSIX",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Multimedia :: Sound/Audio"
    ]


def get_requires(filename):
    """Get the required packages from the pip file."""
    out = []
    with open(filename) as handle:
        for line in handle:
            package, _ = re.split('[^\w]', line, 1)
            out.append(package.strip())
    return out


def get_readme(filename):
    """Get the contents of the README file."""
    with open(filename) as handle:
        return handle.read()


README = get_readme('README.rst')
REQUIRES = get_requires('requires.txt')
RELEASE = '0.2.4'


setup(
    name='avalonms',
    version=RELEASE,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=README,
    author_email=EMAIL,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    url=URL,
    install_requires=REQUIRES,
    packages=find_packages(),
    scripts=[os.path.join('bin', 'avalonmsd')])

