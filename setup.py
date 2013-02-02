#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from __future__ import print_function

import os
import re
import subprocess

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


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
            package, _ = re.split('[^\w\-]', line, 1)
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
VERSION = None

try:
    VERSION = get_contents(_VERSION_FILE)
except IOError:
    pass


setup(
    name='avalonms',
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=README,
    author_email=EMAIL,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    url=URL,
    cmdclass={'version': VersionGenerator},
    install_requires=REQUIRES,
    packages=['avalon', 'avalon.app', 'avalon.tags', 'avalon.web'],
    package_data={'avalon.web': [
            'data/status.html',
            'data/config.ini',
            'data/css/*.css',
            'data/img/*.png',
            'data/js/*.js'
            ]},
    scripts=[os.path.join('bin', 'avalonmsd')])

