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

from setuptools import setup, find_packages, Command


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


_VERSION_FILE = 'VERSION'


def get_requires(filename):
    """Get the required packages from the pip file."""
    out = []
    with open(filename) as handle:
        for line in handle:
            package, _ = re.split('[^\w]', line, 1)
            out.append(package.strip())
    return out


def get_contents(filename):
    """Get the contents of the given file."""
    with open(filename) as handle:
        return handle.read().strip()


def get_version_from_git():
    """Get the current release version from git."""
    proc = subprocess.Popen(
        ['git', 'describe', '--tags', '--abbrev=0'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (out, err) = proc.communicate()
    tag = out.strip()

    if not tag:
        raise ValueError('Could not determine tag: [%s]' % err)        
    try:
        return tag.split('-')[1]
    except ValueError:
        raise ValueError('Could not determine version: [%s]' % tag)


def write_version(filename):
    """Write the current release version from git to a file."""
    with open(filename, 'wb') as handle:
        handle.write(get_version_from_git())


class VersionGenerator(Command):

    """Command to generate the current release from git."""

    description = "Generate the release version from the git tag"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Write the current release version from Git."""
        write_version(_VERSION_FILE)


REQUIRES = get_requires('requires.txt')
README = get_contents('README.rst')
RELEASE = None

try:
    RELEASE = get_contents(_VERSION_FILE)
except IOError:
    pass


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
    cmdclass={'version': VersionGenerator},
    install_requires=REQUIRES,
    packages=find_packages(),
    scripts=[os.path.join('bin', 'avalonmsd')])

