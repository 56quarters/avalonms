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

from distutils.errors import DistutilsOptionError


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
    "Topic :: Multimedia :: Sound/Audio"
    ]


_VERSION_FILE = 'VERSION'


def get_requires(filename):
    """Get the required packages from the pip file."""
    out = []
    with open(filename, 'rb') as handle:
        for line in handle:
            package, _ = re.split('[^\w\-]', line, 1)
            out.append(package.strip())
    return out


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


class StaticCompilation(Command):

    """Command to compress and concatenate CSS and JS"""

    description = "Build static assets for the status page"

    user_options = [
        ('static-base=', None, 'Base directory for CSS and JS directories'),
        ('css-files=', None, 'List of CSS files to concatenate and compress (comma separated, relative to `static-base`)'),
        ('css-output=', None, 'Name of the final CSS output file (file only, no path)'),
        ('js-files=', None, 'List of JS files to concatenate and compress (comma separated, relative to `static-base`)'),
        ('js-output=', None, 'Name of the final JS output file (file only, no path)'),
        ('yui-jar=', None, 'Path to YUI compressor jar')]

    _valid_exts = frozenset(['js', 'css'])

    def initialize_options(self):
        self.static_base = 'avalon/web/data'
        self.css_files = ['css/bootstrap.css', 'css/bootstrap-responsive.css', 'css/avalon.css']
        self.css_output = 'all.min.css'
        self.js_files = ['js/jquery.js', 'js/bootstrap.js', 'js/mustache.js']
        self.js_output = 'all.min.js'
        self.yui_jar = '/opt/yui/current.jar'

    def finalize_options(self):
        self.ensure_dirname('static_base')
        self.ensure_string_list('css_files')
        self.ensure_string_list('js_files')
        self.ensure_filename('yui_jar')

    def _compress(self, contents, out_file):
        """Compress the given contents and write it to the output file."""
        ext = os.path.splitext(out_file)[1].lstrip('.')

        if ext not in self._valid_exts:
            raise DistutilsOptionError(
                "Output file [%s] does not have a valid extension" % out_file)

        full_out_file = os.path.join(self.static_base, ext, out_file)
        proc = subprocess.Popen(
            ['java', '-jar', self.yui_jar, '--type', ext, '-o', full_out_file],
            stdin=subprocess.PIPE, stdout=None, stderr=subprocess.PIPE)

        out, err = proc.communicate(input=contents)
        if 0 != proc.wait():
            raise OSError("Could not minimize %s: %s" % (out_file, err))

    def _compress_all(self, all_files, out_file):
        """Compress the collection of files and write the contents to the
        given output file.
        """
        all_content = []
        for a_file in all_files:
            full_path = os.path.join(self.static_base, a_file)
            with open(full_path, 'rb') as handle:
                all_content.append(handle.read())
        self._compress('\n\n'.join(all_content), out_file)

    def run(self):
        """Compress all CSS and JS files and write them to respective
        single files.
        """
        self._compress_all(self.css_files, self.css_output)
        self._compress_all(self.js_files, self.js_output)


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
    cmdclass={
        'version': VersionGenerator,
        'static': StaticCompilation},
    install_requires=REQUIRES,
    packages=['avalon', 'avalon.app', 'avalon.tags', 'avalon.web'],
    package_data={'avalon.web': [
            'data/status.html',
            'data/config.ini',
            'data/css/*.css',
            'data/js/*.js',
            'data/img/*.png',

            ]},
    scripts=[os.path.join('bin', 'avalonmsd')])

