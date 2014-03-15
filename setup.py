#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


from __future__ import print_function
import subprocess
import sys

import os

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command

AUTHOR = 'TSH Labs'
DESCRIPTION = 'Avalon Music Server'
EMAIL = 'projects@tshlabs.org'
URL = 'http://www.tshlabs.org/'
LICENSE = 'Apache'
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: POSIX",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Multimedia :: Sound/Audio",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7"
]

_VERSION_FILE = 'VERSION'


def get_contents(filename):
    """Get the contents of the given file."""
    with open(filename, 'rb') as handle:
        return handle.read().strip()


class VersionGenerator(Command):
    """Command to generate the current release from git."""

    description = "Generate the release version from a git tag"

    user_options = [
        ('version-file=', None, 'File to write the version number to')]

    def initialize_options(self):
        self.version_file = _VERSION_FILE

    def finalize_options(self):
        # We don't ensure that the version file exists here since
        # we may be creating it for the first time
        pass

    def _get_version_from_git(self):
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

    def _write_version(self, filename):
        """Write the current release version from git to a file."""
        with open(filename, 'wb') as handle:
            handle.write(self._get_version_from_git())

    def run(self):
        """Write the current release version from Git."""
        self._write_version(self.version_file)


# If this is a version of Python prior to 2.7, argparse was
# not included in the standard library and we must list it as
# an installation dependency.
_python_version = (sys.version_info[0], sys.version_info[1])
_argparse_included = (2, 7)

REQUIRES = [
    'cherrypy',
    'mutagen',
    'simplejson',
    'sqlalchemy'
]

if _python_version < _argparse_included:
    REQUIRES.append('argparse')

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
    cmdclass={
        'version': VersionGenerator},
    install_requires=REQUIRES,
    packages=['avalon', 'avalon.app', 'avalon.tags', 'avalon.web'],
    scripts=[os.path.join('bin', 'avalonmsd')])

